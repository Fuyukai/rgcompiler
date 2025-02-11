from pathlib import Path
from typing import cast

import rich
import rich.progress
from lxml.etree import tostring
from rich import print
from tap import Tap

from rgcompiler.tileset import DecompiledTileset, SubtileTileset, decompile_tileset
from rgss import read_object_rgxp
from rgss.rpg.tileset import RubyTileset


class TilesetArgs(Tap):
    game_path: Path  # The path to the game directory.
    output_path: Path = Path.cwd() / "output"
    tileset_name: str | None = None


def write_tileset(
    output_dir: Path,
    decomp: DecompiledTileset | SubtileTileset,
):
    tileset_dir = output_dir
    if isinstance(decomp, SubtileTileset):
        tileset_dir = output_dir / "subtiles"

    output_tsx = tileset_dir / decomp.name.replace("/", "_")
    output_tsx.parent.mkdir(exist_ok=True, parents=True)
    with output_tsx.with_suffix(".tsx").open(mode="wb") as f:
        f.write(
            tostring(decomp.tsx_element, pretty_print=True, xml_declaration=True, encoding="UTF-8")
        )

    output_image_dir = output_dir / "graphics"
    if isinstance(decomp, SubtileTileset):
        output_image_dir = output_image_dir / "subtiles"

    output_image_dir.mkdir(parents=True, exist_ok=True)
    output_image_file = (output_image_dir / output_tsx.stem).with_suffix(".png")
    print(f"writing tileset image to {output_image_file}")

    with output_image_file.open(mode="wb") as f:
        decomp.image.save(f)


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
