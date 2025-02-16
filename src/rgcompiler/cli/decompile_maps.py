from pathlib import Path
from typing import cast

import rich
import rich.progress
from lxml.etree import tostring
from tap import Tap

from rgcompiler.map.decompiler import decompile_map_layout
from rgcompiler.map.tileset import (
    DecompiledTileset,
    SubtileTileset,
    decompile_tileset,
    write_tileset,
)
from rgss import read_object_rgxp
from rgss.rpg.map import RubyRpgMap
from rgss.rpg.tileset import RubyTileset


class MapGenArgs(Tap):
    game_path: Path  # The path to the game directory.
    output_path: Path = Path.cwd() / "output"  # The path to the output project directory.
    map_name: str | None = None


def main() -> int:
    """
    Decompiles a set of maps.
    """

    # https://www.youtube.com/watch?v=hXdPeNeRCuQ

    args = MapGenArgs(underscores_to_dashes=True).parse_args()

    data_dir = args.game_path / "Data"
    raw_tilesets: list[RubyTileset] = cast(
        list[RubyTileset], read_object_rgxp(data_dir / "tilesets.rxdata")
    )

    maps_path = args.output_path / "maps"
    maps_path.mkdir(exist_ok=True, parents=True)

    # only lazily decompile the tilesets because subtile decompilation is relatively intensive
    seen_subtiles: dict[str, SubtileTileset] = {}
    tilesets: dict[str, DecompiledTileset] = {}

    globbed_maps = [i for i in data_dir.glob("Map**.rxdata") if i.name != "MapInfos.rxdata"]

    for map in rich.progress.track(globbed_maps):
        if map.name == "MapInfos.rxdata":
            continue

        if args.map_name and args.map_name != map.stem:
            continue

        read_map = cast(RubyRpgMap, read_object_rgxp(map))
        raw_map_tileset = raw_tilesets[read_map.tileset_id]

        try:
            map_tileset = tilesets[raw_map_tileset.name]
        except KeyError:
            map_tileset = decompile_tileset(args.game_path, raw_map_tileset, seen_subtiles)
            tilesets[raw_map_tileset.name] = map_tileset

        decompiled_map = decompile_map_layout(read_map, map.name, map_tileset)
        saved_path = (maps_path / map.stem).with_suffix(".tmx")

        with saved_path.open(mode="wb") as f:
            f.write(
                tostring(decompiled_map, pretty_print=True, xml_declaration=True, encoding="UTF-8")
            )

    for tileset in tilesets.values():
        write_tileset(args.output_path / "tilesets", tileset)

    for sts in seen_subtiles.values():
        write_tileset(args.output_path / "tilesets", sts)

    return 0
