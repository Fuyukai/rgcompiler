from __future__ import annotations

import csv
from io import StringIO
from pathlib import Path
from typing import TYPE_CHECKING

import structlog

from rgcompiler.map.tileset import DecompiledTileset

if TYPE_CHECKING:
    from lxml.etree import _Element  # type: ignore

from lxml.etree import Element

from rgss.rpg.map import RubyRpgMap

TILESETS_REL_PATH = Path("../tilesets")
SUBTILE_REL_PATH = TILESETS_REL_PATH / "subtiles"


logger: structlog.stdlib.BoundLogger = structlog.get_logger(name=__name__)


def decompile_map_layout(
    original_map: RubyRpgMap,
    map_name: str,
    tileset: DecompiledTileset,
) -> _Element:
    """
    Decompiles the map layout from the Ruby object to a Tiled map.
    """

    root = Element(
        "map",
        version="1.0",
        tiledversion="1.10",
        width=str(original_map.width),
        height=str(original_map.height),
        tilewidth="32",
        tileheight="32",
        nextlayerid="4",
        orientation="orthogonal",
    )

    tlogger = logger.bind(type="tilemap", map_name=map_name)

    ids = tileset.calculate_starting_tile_ids()
    for firstgid, subtiles in zip(ids, tileset.subtiles, strict=False):  # zip_shortest
        source = (SUBTILE_REL_PATH / subtiles.name).with_suffix(".tsx")
        ts_element = Element("tileset", firstgid=str(firstgid), source=str(source))
        tlogger.debug(
            "calculated tileset global id",
            firstgid=firstgid,
            tileset_name=tileset.name,
            subtile_name=subtiles.name,
        )
        root.append(ts_element)

    main_ts_path = (TILESETS_REL_PATH / tileset.name.replace("/", "_")).with_suffix(".tsx")
    main_ts_element = Element("tileset", firstgid=str(ids[-1]), source=str(main_ts_path))
    root.append(main_ts_element)

    tlogger.info("begin decompilation")

    for layer in range(3):
        starting_idx = (original_map.width * original_map.height) * layer

        # tiled supports three formats:
        # 1) individual ``<tile>``. great for if you want the file to be like 300kib long.
        # 2) csv format of tile IDs.
        # 3) base64 blob of 32-bit little endians.
        #
        # in addition, this form can be compressed with zstd or gzip. we use uncompressed csv
        # because it is by far the most compatible with git diffs.

        buf = StringIO()
        writer = csv.writer(buf, lineterminator="\n")

        for y in range(original_map.height):
            row: list[int] = []
            for x in range(original_map.width):
                tile_idx = starting_idx + (y * original_map.width) + x
                rpg_tile_id = original_map.data.raw_data[tile_idx]

                # always map tiles in 0..48 to the blank tile GID. in theory, rpg maker should only
                # emit tiles with tile ID 0, but I'm sure there's some corrupt maps out there that
                # actually use the first block of subtiles to.
                if rpg_tile_id < 48:
                    gid = 0

                elif rpg_tile_id < 384:
                    # autotiles in RPG maker have extra frames to the right for animations.
                    # for tiled tilesets, these are *real* tiles in order to get the animations
                    # showing properly in the editor, so it's not a simple 1<->1 mapping.

                    gid_start = ids[rpg_tile_id // 48]
                    gid = gid_start + (rpg_tile_id % 48)

                else:
                    gid_start = ids[-1]
                    gid = gid_start + rpg_tile_id - 384

                row.append(gid)

            # oh yeah btw tiled csv format doesn't have rows.
            writer.writerow(row)
            buf.write(",")

        layer_el = Element(
            "layer",
            id=str(layer + 1),
            name=f"RPG Maker Layer {layer + 1}",
            width=str(original_map.width),
            height=str(original_map.height),
            x="0",
            y="0",
            visible="1",
        )
        data_el = Element("data", encoding="csv")
        data_el.text = buf.getvalue()
        layer_el.append(data_el)
        root.append(layer_el)

    tlogger.info("end decompilation")

    return root
