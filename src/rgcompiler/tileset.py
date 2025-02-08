from __future__ import annotations

import enum
import itertools
from pathlib import Path
from typing import TYPE_CHECKING

import attrs
import structlog
from PIL.Image import Image, open as open_image

from rgss.rpg.tileset import RubyTileset

if TYPE_CHECKING:
    from lxml.etree import _Element

from lxml.etree import Element

logger: structlog.stdlib.BoundLogger = structlog.get_logger(name=__name__)


def find_image(base_path: Path) -> tuple[Path, Image]:
    paths = [base_path.with_suffix(".png"), base_path.with_suffix(".PNG")]
    for path in paths:
        try:
            return path, open_image(path)
        except FileNotFoundError:
            continue

    raise FileNotFoundError(f"no such PNG image at {base_path}")


@attrs.define(kw_only=True, frozen=True)
class DecompiledTileset:
    """
    The result of a tileset decompilation.
    """

    name: str = attrs.field()
    tsx_element: _Element = attrs.field()

    #: Where the image file for this tileset was located.
    input_image: Path = attrs.field()
    #: Where the image file for the tileset will be written.
    output_image: Path = attrs.field()

    #: The number of tiles in this tileset with animation tiles applied.
    #:
    #: Used to calculate global tile IDs for maps.
    tsx_tile_count: int = attrs.field()

    #: The subtiles for this tileset. Empty for subtiles themselves.
    subtiles: list[DecompiledTileset] = attrs.field(factory=list)

    @property
    def starting_tile_idx(self) -> int:
        """
        Gets the starting tile GID for this tile.
        """

        counter = 0
        for subtile in self.subtiles:
            counter += subtile.tsx_tile_count

        return counter


class SubtileType(enum.Enum):
    SingleTile = 1
    Regular = 4


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


def _make_subtile_tileset(output_graphics_dir: Path, autotile_path: Path) -> DecompiledTileset:
    """
    Makes a new subtile tileset from the given path.
    """

    name = autotile_path.stem

    input_image_path, image = find_image(autotile_path)
    type: SubtileType
    if image.height == 32:
        type = SubtileType.SingleTile
    elif image.height == 128:
        type = SubtileType.Regular
    else:
        raise ValueError(f"Can't process autotile with height of {image.height}")

    tiles_across = image.width // 32
    tile_count = tiles_across * (image.height // 32)
    frame_count = tiles_across // (type.value)
    output_image_path = (output_graphics_dir / autotile_path.stem).with_suffix(".png")

    root = _make_root_element(name, columns=image.width // 32)
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
    if frame_count > 1:
        # OH boy
        #
        for y_tile in range(type.value):
            if type == SubtileType.Regular and y_tile == 0:
                continue

            x_range = 3 if type == SubtileType.Regular else 1

            for x_tile in range(x_range):
                actual_tile_coord = x_tile + (y_tile * tiles_across)
                tile_el = Element("tile", id=str(actual_tile_coord))
                animation = Element("animation")

                for frame in range(frame_count):
                    offset_coord = actual_tile_coord + (x_range * frame)
                    frame_el = Element(
                        "frame", tileid=str(offset_coord), duration=str(1200 // frame_count)
                    )
                    animation.append(frame_el)

                tile_el.append(animation)
                root.append(tile_el)

    return DecompiledTileset(
        name=name,
        tsx_element=root,
        tsx_tile_count=tile_count,
        subtiles=[],
        input_image=input_image_path,
        output_image=output_image_path,
    )


def decompile_tileset(
    input_graphics_dir: Path,
    tileset: RubyTileset,
) -> DecompiledTileset:
    """
    Decompiles an RPG Maker tileset into a set of Tiled tilesets.
    """

    tlogger = logger.bind(tileset_name=tileset.name, type="tileset")

    tlogger.info("begin decompilation", type="tileset", tileset_name=tileset.name)

    # rpg maker (XP) maps are really fucking stupid!
    # here's a list of misfeatures:
    #
    # - autotiles! these are special blocks of 6x8 tiles that can be used to make paths or water
    #   areas in a map automatically. the same thing is achieved by tiled in a less stupid manner
    #   with terrains. WIP on translating them.
    #
    #   autotiles aren't actually stored as a tileset of their own, they're literally just image
    #   files that are referenced from a real tileset.
    #
    # - animations! only autotiles can have animations. they're just stored as another block
    #   directly next to the tile. this is a limit of like eight types of animated tile per
    #   map. even for 2005

    output_graphics = Path("./graphics")
    output_subtiles = output_graphics / "subtiles"
    subtiles: list[DecompiledTileset] = []

    for subtile in tileset.autotile_names:
        if not subtile:
            continue

        stlogger = tlogger.bind(type="subtile", subtile_name=subtile)
        stlogger.info("begin decompilation")

        subtile_path = input_graphics_dir / "Autotiles" / subtile
        subtiles.append(
            _make_subtile_tileset(output_graphics_dir=output_subtiles, autotile_path=subtile_path)
        )
        stlogger.info("completed decompilation")

    image_path = input_graphics_dir / "Tilesets" / tileset.tileset_name
    real_path, image = find_image(image_path)
    output_image_path = (output_graphics / real_path.stem.replace("/", "_")).with_suffix(".png")

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

    ts_properties = Element("properties")
    for idx, subtile in itertools.zip_longest(range(8), subtiles):
        st_name = subtile.name if subtile else ""
        name = f"rgss_subtile_{idx}"
        ts_properties.append(Element("property", name=name, type="string", value=st_name))

    tree.append(ts_properties)

    # skip past the first 384 tiles, as they're subtiles...
    for tile in range(384 + int(tile_count)):
        if tile < 384 and tile % 48 != 0:
            continue

        tile_info = tileset.get_tile_info(tile)
        pairs = [
            ("terrain_tag", tile_info.terrain_tag),
            ("priority", tile_info.priority),
            ("passage_info", tile_info.passage_info),
        ]

        if tile < 384:
            for k, v in pairs:
                prop = Element(
                    "property", name=f"rgss_subtile_{tile // 48}_{k}", type="int", value=str(v)
                )
                ts_properties.append(prop)

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
        input_image=real_path,
        output_image=output_image_path,
        tsx_tile_count=tile_count,
        subtiles=subtiles,
    )
    tlogger.info("completed decompilation")
    return decomp
