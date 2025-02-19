from collections import defaultdict
from collections.abc import Callable
from pathlib import Path
from typing import cast

import click
import structlog
from PIL import Image

from rgcompiler.map.tileset import DecompiledTileset, SubtileTileset, decompile_tileset
from rgcompiler.util import find_image
from rgss import read_object_rgxp
from rgss.rpg.map import RubyRpgMap
from rgss.rpg.tileset import RubyTileset

type TsCache = dict[int, Image.Image]

glogger: structlog.stdlib.BoundLogger = structlog.get_logger(__name__)


def get_tile_image(
    shared_cache: dict[str, TsCache], tileset: DecompiledTileset, idx: int
) -> Image.Image | None:
    # yuck, gotta cache these eventually
    if idx >= 384:
        actual_idx = idx - 384
        image = tileset.image
    elif idx >= 48:
        subtile_group = (idx // 48) - 1
        subtile = tileset.subtiles[subtile_group]
        actual_idx = 0 if subtile.is_single_row else idx % 48
        image = subtile.image
    else:
        # blank tiles
        return None

    try:
        return shared_cache[tileset.name][idx]
    except KeyError:
        pass

    # tilesets are made up of 32x32 tiles, 8 tiles wide. autotiles are 6 tiles tall too.
    col = actual_idx // 8
    row = actual_idx % 8

    col_pos = col * 32
    row_pos = row * 32
    cropped = image.crop((row_pos, col_pos, row_pos + 32, col_pos + 32))
    cropped = cropped.convert("RGBA")
    shared_cache[tileset.name][idx] = cropped
    return cropped


def render_single_map(
    shared_cache: dict[str, TsCache],
    project_directory: Path,
    tilesets: list[DecompiledTileset],
    name: str,
    map: RubyRpgMap,
    *,
    filter_event_images: Callable[[str], bool] | None = None,
) -> Image.Image:
    """
    Renders an RPG Maker XP map to an image.

    If ``filter_event_images`` is provided, this will remove any images that match the provided
    function; useful for filtering out light events that otherwise spam the image.
    """

    tileset = tilesets[map.tileset_id - 1]
    assert tileset
    map_image = Image.new(mode="RGBA", size=(map.width * 32, map.height * 32))

    evt_filter: Callable[[str], bool] = (
        filter_event_images if filter_event_images else lambda it: True
    )

    logger = glogger.bind(map_name=name, tileset=tileset.name)
    logger.info("begin", phase="render")

    for layer in (0, 1, 2):
        logger.info("draw", type="tile", layer=layer)
        for xpos in range(map.width):
            for ypos in range(map.height):
                tile_idx = map.get_tile_at(layer, xpos, ypos)
                tile_image = get_tile_image(shared_cache, tileset, tile_idx)

                if tile_image is None:
                    continue

                pasted_x = xpos * 32
                pasted_y = ypos * 32

                # PIL my behated
                # use the tile image as the mask to correctly blend alpha for higher layers

                mask = tile_image if tile_image.mode == "RGBA" else None  # what the hell, PIL?
                map_image.paste(
                    tile_image, (pasted_x, pasted_y, pasted_x + 32, pasted_y + 32), mask
                )

    for event in map.events.values():
        page = event.pages[0]

        elogger = logger.bind(type="event", name=event.name, x=event.x, y=event.y)

        if page.graphic.tile_id:
            evt_image = get_tile_image(shared_cache, tileset, page.graphic.tile_id)

            if not evt_image:
                continue

            elogger.info("draw", tile_id=page.graphic.tile_id)
            map_image.paste(evt_image, (event.x * 32, event.y * 32), mask=evt_image)

        elif page.graphic.character_name and evt_filter(page.graphic.character_name):
            image_path = project_directory / "Graphics" / "Characters" / page.graphic.character_name
            character_image = find_image(image_path)
            # weird as hell fucking rpg maker format
            # don't think direction can ever be a diagonal...
            across_size = character_image.width // 4
            down_size = character_image.height // 4
            image_y = down_size * ((page.graphic.direction.value // 2) - 1)
            image_x = across_size * (page.graphic.pattern)
            evt_image = character_image.crop(
                box=(image_x, image_y, image_x + across_size, image_y + down_size)
            )
            evt_image = evt_image.convert("RGBA")

            if page.graphic.opacity != 255:
                old = evt_image.copy()
                old.putalpha(page.graphic.opacity)
                evt_image.paste(old, mask=evt_image)

            width_left = (event.x) * 32
            width_right = ((event.x) * 32) + evt_image.width

            # this is kinda gross...
            # large character images *seem* to be done by centering, but for images that fit below
            # two tiles they are placed directly onto the tile signified by the event.
            # is there a better way to do this?
            if evt_image.width >= 64:
                width_left -= evt_image.width // 2
                width_right -= evt_image.width // 2

            height_left = ((event.y + 1) * 32) - evt_image.height
            height_right = (event.y + 1) * 32

            box = (
                width_left,
                height_left,
                width_right,
                height_right,
            )

            elogger.info(
                "draw",
                character_name=page.graphic.character_name,
                direction=str(page.graphic.direction),
                pattern=page.graphic.pattern,
            )

            map_image.paste(evt_image, box=box, mask=evt_image)

    logger.info("end", phase="render")

    return map_image


@click.command("render-image")
@click.argument(
    "input_directory",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    required=True,
)
@click.argument("map_idx", type=int)
def main(input_directory: Path, map_idx: int):
    shared_cache: dict[str, TsCache] = defaultdict(dict)

    tilesets_file = input_directory / "Data" / "tilesets.rxdata"
    raw_tilesets = cast(list[RubyTileset], read_object_rgxp(tilesets_file))[1:]
    seen_subtiles: dict[str, SubtileTileset] = {}
    tilesets = [
        decompile_tileset(input_directory, ts, seen_subtiles) for ts in raw_tilesets if ts.name
    ]

    map_file = input_directory / "Data" / f"Map{map_idx:03d}.rxdata"
    rpg_map = cast(RubyRpgMap, read_object_rgxp(map_file))
    image = render_single_map(
        shared_cache,
        input_directory,
        tilesets,
        map_file.stem,
        rpg_map,
    )

    with Path("./out.png").open(mode="wb") as f:
        image.save(f)


if __name__ == "__main__":
    main()
