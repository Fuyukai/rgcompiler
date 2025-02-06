from pathlib import Path
from typing import cast

import PIL
import PIL.Image
import rich
import rich.progress
from lxml.etree import Element, tostring
from rich import print
from tap import Tap

from rgss import read_object_rgxp
from rgss.rpg.tileset import RubyTileset


class TilesetArgs(Tap):
    game_path: Path  # The path to the game directory.
    output_path: Path = Path.cwd() / "output"


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

        if not tileset.tileset_name:
            print(f"skipping tileset {tileset.id} with empty name (?)")
            continue

        print(f"generating tileset [cyan]{tileset.name}[/cyan]...")
        root_ts_path = graphics_path / "Tilesets" / tileset.tileset_name
        find_ts_paths = [root_ts_path.with_suffix(".png"), root_ts_path.with_suffix(".PNG")]

        for image_path in find_ts_paths:
            try:
                image = PIL.Image.open(image_path)
                break
            except FileNotFoundError:
                continue
        else:
            print(f" ! [red]couldn't load tileset image[/red]: {tileset.tileset_name}")
            continue

        output_image_name = image_path.with_suffix(".png").name
        output_image_path = out_tilesets / "graphics" / output_image_name

        assert (image.width / 32) == 8.0, "tileset should be exactly 8 tiles across"
        tile_count = (image.height / 8) * (image.width / 8)
        assert tile_count.is_integer(), f"tileset has odd dimensions {(image.height, image.width)}"

        tree = Element("tileset")
        tree.attrib.update({
            "version": "1.10",
            "name": tileset.name,
            "tilewidth": "32",
            "tileheight": "32",
            # default values but let's incl them just to be safe
            "spacing": "0",
            "margin": "0",
            # user-editable, but this is fine as it's always 8 for the genned image
            "columns": "8",
        })
        image_el = Element("image")
        image_el.attrib.update({
            "source": str(output_image_path.relative_to(out_tilesets)),
            "width": str(image.width),
            "height": str(image.height),
        })
        tree.append(image_el)

        output_tileset_path = (out_tilesets / tileset.name.replace("/", "_")).with_suffix(".tsx")
        output_tileset_path.write_bytes(
            tostring(tree, pretty_print=True, xml_declaration=True, encoding="UTF-8")
        )
        print(f" written tsx file {output_tileset_path}")

        with output_image_path.open(mode="wb") as f:
            image.save(f, format="png")

        print(f" copied image file {output_image_path}")

    return 0
