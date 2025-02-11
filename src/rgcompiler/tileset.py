from __future__ import annotations

import enum
import itertools
from pathlib import Path
from typing import TYPE_CHECKING

import attrs
import structlog
from PIL.Image import Image, new as new_image

from rgcompiler.util import find_image
from rgss.rpg.tileset import RubyTileset

if TYPE_CHECKING:
    from lxml.etree import _Element

from lxml.etree import Element

TILE_SIZE = 16
OUTPUT_WIDTH = 8
OUTPUT_HEIGHT = 6

# fmt: off
TILE_MAPPING = [
    [26, 27, 32, 33], [4, 27, 32, 33], [26, 5, 32, 33], [4, 5, 32, 33], [26, 27, 32, 11], [4, 27, 32, 11], [26, 5, 32, 11], [4, 5, 32, 11],  # noqa: E501
    [26, 27, 10, 33], [4, 27, 10, 33], [26, 5, 10, 33], [4, 5, 10, 33], [26, 27, 10, 11], [4, 27, 10, 11], [26, 5, 10, 11], [4, 5, 10, 11],  # noqa: E501
    [24, 25, 30, 31], [24, 5, 30, 31], [24, 25, 30, 31], [24, 5, 30, 11], [14, 15, 20, 21], [14, 15, 20, 11], [14, 15, 10, 21], [14, 15, 10, 11],  # noqa: E501
    [28, 29, 34, 35], [28, 29, 10, 35], [4, 29, 34, 35], [4, 29, 10, 35], [38, 39, 44, 45], [4, 39, 44, 45], [38, 5, 44, 45], [4, 5, 44, 45],  # noqa: E501
    [24, 29, 30, 35], [14, 15, 44, 45], [12, 13, 18, 19], [12, 13, 18, 11], [16, 17, 22, 23], [16, 17, 10, 23], [40, 41, 46, 47], [4, 41, 46, 47],  # noqa: E501
    [36, 37, 42, 43], [36, 5, 42, 43], [12, 17, 18, 23], [12, 13, 42, 43], [36, 41, 42, 47], [17, 17, 46, 47], [12, 13, 42, 47], [0, 1, 6, 7],  # noqa: E501
]
# fmt: on


logger: structlog.stdlib.BoundLogger = structlog.get_logger(name=__name__)


@attrs.define(kw_only=True, frozen=True)
class DecompiledTileset:
    """
    The result of a tileset decompilation.
    """

    name: str = attrs.field()
    tsx_element: _Element = attrs.field()

    #: The real loaded image for this tileset.
    image: Image = attrs.field()

    #: The number of tiles in this tileset with animation tiles applied.
    #:
    #: Used to calculate global tile IDs for maps.
    tsx_tile_count: int = attrs.field()

    #: The subtiles for this tileset. Empty for subtiles themselves.
    subtiles: list[SubtileTileset] = attrs.field(factory=list)

    @property
    def starting_tile_idx(self) -> int:
        """
        Gets the starting tile GID for this tile.
        """

        return len(self.subtiles) * 48


@attrs.define(kw_only=True, frozen=True)
class SubtileTileset:
    """
    A decompressed and unpacked subtile tileset.
    """

    name: str = attrs.field()
    tsx_element: _Element = attrs.field()
    image: Image = attrs.field()


class SubtileType(enum.Enum):
    SingleTile = 1
    Regular = 8


def _make_root_element(name: str, *, columns: int = 8):
    return Element(
        "tileset",
        version="1.10",
        name=name,
        tilewidth="32",
        tileheight="32",
        spacing="0",
        margin="0",
        columns=str(columns),
    )


def _decompress_autotile_image(tileset: Image) -> Image:
    # tileset = tileset.convert("RGBA")
    parts: list[Image] = []
    tileset.save("/tmp/rgd/input.png")

    for y in range(0, 128, TILE_SIZE):
        for x in range(0, 96, TILE_SIZE):
            bounding_box = (x, y, x + TILE_SIZE, y + TILE_SIZE)
            parts.append(tileset.crop(bounding_box))

    out_image = new_image(
        mode="RGBA", size=(2 * OUTPUT_WIDTH * TILE_SIZE, 2 * OUTPUT_HEIGHT * TILE_SIZE)
    )

    for y, row in enumerate(itertools.batched(TILE_MAPPING, OUTPUT_WIDTH, strict=True)):
        for x, square in enumerate(row):
            for i, part in enumerate(square):
                dy, dx = divmod(i, 2)
                box = ((2 * x + dx) * TILE_SIZE, (2 * y + dy) * TILE_SIZE)
                out_image.paste(parts[part], box=box, mask=parts[part])

    return out_image


def _make_subtile_tileset_v2(autotile_path: Path) -> SubtileTileset:
    """
    Makes a new subtile tileset from the given path.
    """

    name = autotile_path.stem.replace("/", "_")
    original_image = find_image(autotile_path)
    output_image_path = (Path("graphics/subtiles") / name).with_suffix(".png")

    type: SubtileType
    frames: int
    if original_image.height == 32:
        type = SubtileType.SingleTile
        frames = original_image.width // 32
        image = original_image
    elif original_image.height == 128:
        type = SubtileType.Regular
        frames = original_image.width // 96
        image = new_image("RGBA", (frames * (OUTPUT_WIDTH * 32), OUTPUT_HEIGHT * 32))

        for slice in range(0, original_image.width, 96):
            subtile_frame = original_image.crop((slice, 0, slice + 96, 128))
            decomp = _decompress_autotile_image(subtile_frame)
            image.paste(decomp, ((slice // 96) * 256, 0))

    else:
        raise ValueError(f"Can't process autotile with height of {original_image.height}")

    root = _make_root_element(name, columns=image.width // 16)
    image_el = Element(
        "image",
        source="../" + str(output_image_path),
        width=str(image.width),
        height=str(image.height),
    )
    root.append(image_el)

    # frame count of 1 means no animations, so we don't need to add any animation objects to the
    # final tiles.
    #
    # in addition, passage data is provided by the parent tileset, not this tileset, so there's no
    # extra frames to be added; so, no point adding tile elements.
    if frames > 1 and type == SubtileType.Regular:
        # the way this works is that every tile has another tile (8 * frames * 32) tiles along
        for y in range(6):
            for x in range(8):
                actual_tile_coord = x + (y * (frames * 8))
                tile_el = Element("tile", id=str(actual_tile_coord))
                animation = Element("animation")

                for frame in range(frames):
                    offset_coord = actual_tile_coord + (8 * frame)
                    frame_el = Element(
                        "frame", tileid=str(offset_coord), duration=str(1200 // frames)
                    )
                    animation.append(frame_el)

                tile_el.append(animation)
                root.append(tile_el)

    elif frames > 1 and type == SubtileType.SingleTile:
        tile_el = Element("tile", id="0")
        animation = Element("animation")
        for count in range(frames):
            animation.append(Element("frame", tileid=str(count), duration=str(1200 // frames)))

        tile_el.append(animation)
        root.append(tile_el)

    return SubtileTileset(name=name, tsx_element=root, image=image)


def decompile_tileset(
    input_project_dir: Path, tileset: RubyTileset, seen_subtiles: dict[str, SubtileTileset]
) -> DecompiledTileset:
    """
    Decompiles an RPG Maker tileset into a set of Tiled tilesets.
    """

    tlogger = logger.bind(tileset_name=tileset.name, type="tileset")

    tlogger.info("begin decompilation", type="tileset", tileset_name=tileset.name)

    # rpg maker (XP) maps are really fucking stupid!
    # here's a list of misfeatures:
    #
    # - autotiles! these are special blocks of 3x4 tiles that can be used to make paths or water
    #   areas in a map automatically. the same thing is achieved by tiled in a less stupid manner
    #   with terrains. WIP on translating them.
    #
    #   autotiles aren't actually stored as a tileset of their own, they're literally just image
    #   files that are referenced from a real tileset.
    #
    # - animations! only autotiles can have animations. they're just stored as another block
    #   directly next to the tile. this is a limit of like eight types of animated tile per
    #   map. this is stingy even for 2005!
    #
    # - every map has an implicit autotile for tile zero, which is blank. this means the first
    #   47 (!) ids are just unused.

    input_graphics_dir = input_project_dir / "Graphics"
    output_graphics_dir = Path("./graphics")
    subtiles: list[SubtileTileset] = []

    for subtile_name in tileset.autotile_names:
        if not subtile_name:
            continue

        try:
            subtiles.append(seen_subtiles[subtile_name])
        except KeyError:
            pass
        else:
            continue

        stlogger = tlogger.bind(type="subtile", subtile_name=subtile_name)
        stlogger.info("begin decompilation")

        subtile_path = input_graphics_dir / "Autotiles" / subtile_name
        subtile = _make_subtile_tileset_v2(subtile_path)
        subtiles.append(subtile)
        stlogger.info("completed decompilation")
        seen_subtiles[subtile_name] = subtile

    image_path = input_graphics_dir / "Tilesets" / tileset.tileset_name
    image = find_image(image_path)
    output_image_path = (output_graphics_dir / tileset.name.replace("/", "_")).with_suffix(".png")

    width, height = image.size
    assert width == 8 * 32, (
        f"expected root tileset image to be 256px wide, is actually {width} ({width / 32} tiles?)"
    )
    tile_count = (height // 32) * (width // 32)

    tree = _make_root_element(name=tileset.name, columns=8)
    tree.append(
        Element(
            "image", source=str(output_image_path), width=str(image.width), height=str(image.height)
        )
    )

    tileset_props = Element("properties")
    for idx, subtile in itertools.zip_longest(range(7), subtiles):
        st_name = subtile.name if subtile else ""
        name = f"rgss_subtile_{idx + 1}"
        tileset_props.append(Element("property", name=name, type="string", value=st_name))

    tree.append(tileset_props)

    for tile in range(384 + int(tile_count)):
        if tile < 384 and tile % 48 != 0:
            # Subtiles inherit their properties from the first subtile ID in the list.
            continue

        tile_info = tileset.get_tile_info(tile)
        pairs = [
            ("terrain_tag", tile_info.terrain_tag),
            ("priority", tile_info.priority),
            ("passage_info", tile_info.passage_info),
        ]

        if tile < 384:
            # Subtiles are stored in a separate tileset but can have per-tileset metadata, so these
            # are stored in the *parent* tileset instead.
            for k, v in pairs:
                prop = Element(
                    "property", name=f"rgss_subtile_{tile // 48}_{k}", type="int", value=str(v)
                )
                tileset_props.append(prop)

        else:
            tile_el = Element("tile", id=str(tile - 384))
            tile_el.attrib["id"] = str(tile - 384)

            prop = Element("properties")

            for k, v in pairs:
                prop.append(Element("property", name=f"rgss_{k}", type="int", value=str(v)))

            tile_el.append(prop)
            tree.append(tile_el)

    decomp = DecompiledTileset(
        name=tileset.name,
        tsx_element=tree,
        image=image,
        tsx_tile_count=tile_count,
        subtiles=subtiles,
    )
    tlogger.info("completed decompilation")
    return decomp
