from pathlib import Path
from typing import cast

import rich
import rich.progress
from rich import print
from tap import Tap

from rgcompiler.map.tileset import SubtileTileset, decompile_tileset, write_tileset
from rgss import read_object_rgxp
from rgss.rpg.tileset import RubyTileset


class TilesetArgs(Tap):
    game_path: Path  # The path to the game directory.
    output_path: Path = Path.cwd() / "output"
    tileset_name: str | None = None


def main() -> int:
    """
    Generates Tiled tileset files when given a RGXP game directory.
    """

    args = TilesetArgs(underscores_to_dashes=True).parse_args()

    tilesets = args.game_path / "Data" / "tilesets.rxdata"
    obb = cast(list[RubyTileset | None], read_object_rgxp(tilesets.read_bytes()))

    out = args.output_path
    out_tilesets = out / "tilesets"
    (out_tilesets / "graphics").mkdir(exist_ok=True, parents=True)

    seen_subtiles: dict[str, SubtileTileset] = {}

    for tileset in rich.progress.track(obb):
        # for whatever reason, ``tilesets.rxdata`` always has an empty tileset as the first one
        if tileset is None:
            continue

        if args.tileset_name and tileset.name != args.tileset_name:
            continue

        if not tileset.tileset_name:
            print(f"skipping tileset {tileset.id} with empty name (?)")
            continue

        ts = decompile_tileset(args.game_path, tileset, seen_subtiles=seen_subtiles)

        write_tileset(out_tilesets, ts)

    for subtileset in rich.progress.track(seen_subtiles.values(), description="Saving subtiles..."):
        write_tileset(out_tilesets, subtileset)

    return 0
