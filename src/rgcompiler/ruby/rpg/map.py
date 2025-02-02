from typing import final, override

import attrs

from rgcompiler.ruby.rgss import RgssTable
from rgcompiler.ruby.rpg.misc import RubyAudioFile
from rhodochrosite.ruby import (
    GenericRubyUserObject,
    RubyMarshalValue,
    RubySymbol,
    RubyUserObject,
    atom,
)

RPG_MAP = atom("RPG::Map")


@attrs.define(slots=True)
@final
class RubyRpgMap(RubyUserObject):
    """
    The most fundamental unit of an RPG maker game; the map.

    A map is a collection of two things: a list of tiles (stored in the ``data`` table) and a list
    of events (stored in the ``events`` dict). Maps also have an associated set of music, and for
    regular RPG Maker games a list of encounters (but this field is unused for Reborn-style games).

    Please note that the map's name is stored separately to the map file itself.
    """

    # Notes:
    # - I don't know why ``width`` and ``height`` are duplicated.

    #: The ID of the tileset for this map.
    tileset_id: int = attrs.field()

    #: The width of this map in tiles.
    width: int = attrs.field()
    #: The height of this map in tiles.
    height: int = attrs.field()

    #: If True, the background music will be automatically played when this map is loaded.
    autoplay_bgm: bool = attrs.field()

    #: The background music object for this map.
    bgm: RubyAudioFile = attrs.field()

    #: If True, the background sounds (?) will be automatically played when this map is loaded.
    autoplay_bgs: bool = attrs.field()

    #: The background sound (?) object for this map.
    bgs: RubyAudioFile = attrs.field()

    #: The RGSS table containing the tiles for this map.
    data: RgssTable = attrs.field()

    #: A mapping of [event id: event] for this map.
    events: dict[str, GenericRubyUserObject] = attrs.field()

    # unused by reborn
    encounter_list: list[RubyMarshalValue] = attrs.field()
    encounter_step: int = attrs.field()

    def __attrs_post_init__(self):
        assert self.data.row_count == self.width
        assert self.data.column_count == self.height

    @property
    @override
    def ruby_class_name(self) -> RubySymbol:
        return RPG_MAP
