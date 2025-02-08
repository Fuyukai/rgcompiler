import shutil
from pathlib import Path
from typing import cast

import rich
import rich.progress
from lxml.etree import tostring
from rich import print
from tap import Tap

from rgcompiler.tileset import DecompiledTileset, decompile_tileset
from rgss import read_object_rgxp
from rgss.rpg.tileset import RubyTileset


class TilesetArgs(Tap):
    game_path: Path  # The path to the game directory.
    output_path: Path = Path.cwd() / "output"
    tileset_name: str | None = None


def write_tileset(
    output_dir: Path,
    decomp: DecompiledTileset,
    is_subtile: bool = False,
):
    if is_subtile:
        of = output_dir / "subtiles" / decomp.name.replace("/", "_")
        of.mkdir(parents=True, exist_ok=True)
    else:
        of = output_dir / decomp.name.replace("/", "_")

    with of.with_suffix(".tsx").open(mode="wb") as f:
        f.write(
            tostring(decomp.tsx_element, pretty_print=True, xml_declaration=True, encoding="UTF-8")
        )

    output = output_dir / decomp.output_image
    output.parent.mkdir(parents=True, exist_ok=True)
    print(f"copy: {decomp.input_image} -> {output}")
    shutil.copy(decomp.input_image, output)

    for subtile in decomp.subtiles:
        write_tileset(output_dir, subtile, is_subtile=True)


def main() -> int:
    """
    Generates Tiled tileset files when given a RGXP game directory.
    """

    args = TilesetArgs(underscores_to_dashes=True).parse_args()

    tilesets = args.game_path / "Data" / "tilesets.rxdata"
    graphics_path = args.game_path / "Graphics"
    obb = cast(list[RubyTileset | None], read_object_rgxp(tilesets.read_bytes()))

    out = args.output_path
    out_tilesets = out / "tilesets"
    (out_tilesets / "graphics").mkdir(exist_ok=True, parents=True)

    for tileset in rich.progress.track(obb):
        # for whatever reason, ``tilesets.rxdata`` always has an empty tileset as the first one
        if tileset is None:
            continue

        if args.tileset_name and tileset.name != args.tileset_name:
            continue

        if not tileset.tileset_name:
            print(f"skipping tileset {tileset.id} with empty name (?)")
            continue

        ts = decompile_tileset(graphics_path, tileset)

        write_tileset(out_tilesets, ts)

    return 0
