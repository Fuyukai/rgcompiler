import os
from pathlib import Path

import pytest

from rgss import read_object_rgxp, write_object_rgxp
from rgss.rpg.commands.misc import SetMoveRouteCommand, VisualMoveRouteCommand
from rgss.rpg.event import (
    RPG_EVENT,
    RPG_EVENT_CONDITION,
    RPG_EVENT_GRAPHIC,
    RPG_EVENT_PAGE,
    RubyEventGraphic,
    RubyEventPage,
    RubyEventPageCondition,
    RubyRpgEvent,
)
from rgss.rpg.map import RPG_MAP, RubyRpgMap
from rgss.rpg.misc import RPG_AUDIOFILE, RubyAudioFile
from rgss.rpg.moves import RPG_MOVE_ROUTE, RubyMoveRoute
from rgss.types import COLOUR_TYPE, TABLE_TYPE, TONE_TYPE, RgssColour, RgssTable, RgssTone
from rhodochrosite.reader import MarshalReader
from rhodochrosite.ruby import GenericRubyUserObject, make_ruby_attrs_object_fn

ROOT_MAP_PATH = os.environ.get("TEST_RGSS_MAP_PATH")


def _gather_map_paths() -> list[Path]:
    if ROOT_MAP_PATH is None:
        return []

    root_path = Path(ROOT_MAP_PATH)
    return [path for path in root_path.glob("Map**.rxdata") if path.name != "MapInfos.rxdata"]


def _map_idfn(path: Path) -> str:
    return path.name


@pytest.mark.skipif(ROOT_MAP_PATH is None, reason="TEST_RGSS_MAP_PATH env var isn't set")
@pytest.mark.parametrize("map_path", _gather_map_paths(), ids=_map_idfn)
def test_map_roundtrips(map_path: Path):
    """
    Tests if a map's events successfully roundtrip.
    """

    # The command reading and writing methods are both tested normally by running through the
    # read -> write -> read cycle, then both reading and writing are tested by verifying a complete
    # cycle matches a reader without the ability to load command types.
    #
    # If they don't match, then either the reader or writer for that command doesn't match!

    raw = map_path.read_bytes()
    written_1 = write_object_rgxp(read_object_rgxp(raw))

    reader = MarshalReader.from_bytes(raw, decode_all_strings=True)

    reader.object_factories[RPG_AUDIOFILE] = make_ruby_attrs_object_fn(RubyAudioFile)
    reader.object_factories[RPG_MAP] = make_ruby_attrs_object_fn(RubyRpgMap)
    reader.object_factories[RPG_EVENT] = make_ruby_attrs_object_fn(RubyRpgEvent)
    reader.object_factories[RPG_EVENT_PAGE] = make_ruby_attrs_object_fn(RubyEventPage)
    reader.object_factories[RPG_EVENT_CONDITION] = make_ruby_attrs_object_fn(RubyEventPageCondition)
    reader.object_factories[RPG_EVENT_GRAPHIC] = make_ruby_attrs_object_fn(RubyEventGraphic)
    reader.object_factories[RPG_MOVE_ROUTE] = make_ruby_attrs_object_fn(RubyMoveRoute)
    reader.custom_factories[TABLE_TYPE] = RgssTable.make_rgss_table
    reader.custom_factories[COLOUR_TYPE] = RgssColour.from_bytes
    reader.custom_factories[TONE_TYPE] = RgssTone.from_bytes

    read_normal = reader.next_object()
    read_rgxp = read_object_rgxp(written_1)

    assert isinstance(read_normal, RubyRpgMap), "normal map wasn't an rpg map!"
    assert isinstance(read_rgxp, RubyRpgMap), "what the fuck?"

    for ev_id, ev_normal in read_normal.events.items():
        ev_rgxp = read_rgxp.events[ev_id]

        assert ev_normal.id == ev_rgxp.id

        for page_normal, page_rgxp in zip(ev_normal.pages, ev_rgxp.pages, strict=True):
            assert page_normal.graphic == page_rgxp.graphic

            # key difference here is that the normal pages will be GenericRubyUserObject!
            for command_normal, command_rgxp in zip(
                page_normal.commands, page_rgxp.commands, strict=True
            ):
                assert isinstance(command_normal, GenericRubyUserObject)
                raw = command_rgxp.to_raw_command()
                code = command_normal.get_ivar("@code")
                assert code == raw.code, f"code didn't match for {command_rgxp}"
                indent = command_normal.get_ivar("@indent")
                assert indent == raw.indent, f"indent didn't match for {command_rgxp}!"

                if isinstance(command_rgxp, (SetMoveRouteCommand, VisualMoveRouteCommand)):
                    # TODO!
                    continue

                # now the scary one...
                parameters = command_normal.get_ivar("@parameters")
                assert parameters == raw.parameters, f"params didn't match for {command_rgxp}"
