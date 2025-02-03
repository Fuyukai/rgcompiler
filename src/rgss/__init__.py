from __future__ import annotations

from io import BytesIO

from rgss.rpg import (
    RPG_AUDIOFILE,
    RPG_EVENT,
    RPG_EVENT_CONDITION,
    RPG_EVENT_GRAPHIC,
    RPG_EVENT_PAGE,
    RPG_MAP,
    RPG_TILESET,
    RubyAudioFile as RubyAudioFile,
    RubyEventGraphic as RubyEventGraphic,
    RubyEventPage as RubyEventPage,
    RubyEventPageCondition as RubyEventPageCondition,
    RubyMoveRoute as RubyMoveRoute,
    RubyRpgEvent as RubyRpgEvent,
    RubyRpgMap as RubyRpgMap,
    RubyTileset as RubyTileset,
)
from rgss.rpg.commands import make_event_command_from_ivars
from rgss.rpg.commands.base import RPG_EVENT_COMMAND
from rgss.rpg.moves import RPG_MOVE_ROUTE
from rgss.types import (
    COLOUR_TYPE,
    TABLE_TYPE,
    TONE_TYPE,
    RgssColour as RgssColour,
    RgssTable as RgssTable,
    RgssTone as RgssTone,
)
from rhodochrosite.cursor import Cursor
from rhodochrosite.reader import MarshalReader
from rhodochrosite.ruby import RubyMarshalValue, make_ruby_attrs_object_fn
from rhodochrosite.writer import MarshalWriter


def add_all_ruby_types(reader: MarshalReader) -> None:  # pragma: no cover
    """
    Adds all ruby types to the marshal reader.
    """

    reader.custom_factories[TABLE_TYPE] = RgssTable.make_rgss_table
    reader.custom_factories[COLOUR_TYPE] = RgssColour.from_bytes
    reader.custom_factories[TONE_TYPE] = RgssTone.from_bytes

    reader.object_factories[RPG_AUDIOFILE] = make_ruby_attrs_object_fn(RubyAudioFile)
    reader.object_factories[RPG_TILESET] = make_ruby_attrs_object_fn(RubyTileset)
    reader.object_factories[RPG_MAP] = make_ruby_attrs_object_fn(RubyRpgMap)
    reader.object_factories[RPG_EVENT] = make_ruby_attrs_object_fn(RubyRpgEvent)
    reader.object_factories[RPG_EVENT_PAGE] = make_ruby_attrs_object_fn(RubyEventPage)
    reader.object_factories[RPG_EVENT_CONDITION] = make_ruby_attrs_object_fn(RubyEventPageCondition)
    reader.object_factories[RPG_EVENT_GRAPHIC] = make_ruby_attrs_object_fn(RubyEventGraphic)
    reader.object_factories[RPG_EVENT_COMMAND] = make_event_command_from_ivars
    reader.object_factories[RPG_MOVE_ROUTE] = make_ruby_attrs_object_fn(RubyMoveRoute)


def make_reader(data: bytes) -> MarshalReader:  # pragma: no cover
    reader = MarshalReader(stream=Cursor(wrapped=data), decode_all_strings=True)
    add_all_ruby_types(reader)
    return reader


def read_object_rgxp(data: bytes) -> RubyMarshalValue:  # pragma: no cover
    reader = make_reader(data)
    return reader.next_object()


def write_object_rgxp(data: RubyMarshalValue) -> bytes:  # pragma: no cover
    buf = BytesIO()
    writer = MarshalWriter(buffer=buf)
    writer.write_object(data)
    return buf.getvalue()
