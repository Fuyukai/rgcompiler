from __future__ import annotations

from typing import TYPE_CHECKING, cast, final, override

import attr

if TYPE_CHECKING:
    from lxml.etree import _Element

import attrs
from lxml.etree import Element

from rhodochrosite.ruby import (
    RubyMarshalValue,
    RubySymbol,
    RubyUserObject,
    atom,
    ruby_converter,
    ruby_name,
)

RPG_AUDIOFILE = atom("RPG::AudioFile")
RPG_SYSTEM = atom("RPG::System")
RPG_SYSTEM_WORDS = atom("RPG::System::Words")
RPG_SYSTEM_TESTBATTLER = atom("RPG::System::TestBattler")


@attr.define(slots=True, kw_only=True)
@final
class RubyAudioFile(RubyUserObject):
    """
    References an audio file in the RPG Maker database.
    """

    #: The name of this file in the database, e.g. ``"Atmosphere- Dark Crystal"``.
    name: str = attr.field()

    #: The volume as a number between 0 to 100, with 0 being silent and 100 being maximum.
    volume: int = attr.field()

    #: The pitch as a number between 0 and 100.
    pitch: int = attr.field()

    def as_tiled_properties(
        self,
        name: str,
        autoplay: bool,
    ) -> _Element:
        """
        Turns this into a custom ``RPG::AudioFile`` property for Tiled maps.
        """

        element = Element("property", name=name, type="class", propertytype=RPG_AUDIOFILE.value)
        props = [
            ("name", self.name),
            ("volume", str(self.volume)),
            ("pitch", str(self.pitch)),
            ("autoplay", str(autoplay)),
        ]
        subprops = Element("properties")

        for prop_name, prop_value in props:
            sub_element = Element("property", name=prop_name, value=prop_value)
            subprops.append(sub_element)

        element.append(subprops)

        return element

    @property
    @override
    def ruby_class_name(self):
        return RPG_AUDIOFILE


def _drop_first(data: list[str | None]) -> list[str]:
    if data[0] is not None:
        return data  # type: ignore

    return cast(list[str], data[1:])


def _re_add_first(data: RubyMarshalValue) -> list[str | None]:
    return [None, *cast(list[str], data)]


@attrs.define(frozen=True)
class RubyRpgWords(RubyUserObject):
    # ?
    str_: str = attrs.field(metadata=ruby_name("str"))
    armor3: str = attrs.field()
    gold: str = attrs.field()
    sp: str = attrs.field()
    mdef: str = attrs.field()
    int: str = attrs.field()
    skill: str = attrs.field()
    armor2: str = attrs.field()
    hp: str = attrs.field()
    pdef: str = attrs.field()
    equip: str = attrs.field()
    agi: str = attrs.field()
    attack: str = attrs.field()
    armor1: str = attrs.field()
    atk: str = attrs.field()
    item: str = attrs.field()
    dex: str = attrs.field()
    armor4: str = attrs.field()
    weapon: str = attrs.field()
    guard: str = attrs.field()

    @property
    @override
    def ruby_class_name(self) -> RubySymbol:
        return RPG_SYSTEM_WORDS


@attrs.define(frozen=True)
class RubyRpgTestBattler(RubyUserObject):
    # idk what the fuck this is lol
    actor_id: int = attrs.field()
    armor4_id: int = attrs.field()
    weapon_id: int = attrs.field()
    level: int = attrs.field()
    armor3_id: int = attrs.field()
    armor2_id: int = attrs.field()
    armor1_id: int = attrs.field()

    @property
    @override
    def ruby_class_name(self) -> RubySymbol:
        return RPG_SYSTEM_TESTBATTLER


@attrs.define(kw_only=True)
@final
class RubyRpgSystem(RubyUserObject):
    """
    Type for the root element of ``System.rxdata`` files.
    """

    #: The list of global variable names.
    variables: list[str] = attrs.field(
        converter=_drop_first, metadata=ruby_converter(_re_add_first)
    )

    #: The list of global switch names.
    switches: list[str] = attrs.field(converter=_drop_first, metadata=ruby_converter(_re_add_first))

    # various sound effects
    cancel_se: RubyAudioFile = attrs.field()
    battle_end_me: RubyAudioFile = attrs.field()
    escape_se: RubyAudioFile = attrs.field()
    decision_se: RubyAudioFile = attrs.field()
    battle_bgm: RubyAudioFile = attrs.field()
    battle_start_se: RubyAudioFile = attrs.field()
    equip_se: RubyAudioFile = attrs.field()
    cursor_se: RubyAudioFile = attrs.field()
    enemy_collapse_se: RubyAudioFile = attrs.field()
    # hey, this one is actually used!
    title_bgm: RubyAudioFile = attrs.field()
    load_se: RubyAudioFile = attrs.field()
    # as is this one!
    buzzer_se: RubyAudioFile = attrs.field()
    gameover_me: RubyAudioFile = attrs.field()
    actor_collapse_se: RubyAudioFile = attrs.field()
    save_se: RubyAudioFile = attrs.field()
    shop_se: RubyAudioFile = attrs.field()

    # wtf is this?
    # this field is quite literally called fucking underscore.
    _: int = attrs.field(alias="_")
    magic_number: int = attrs.field()

    # rpg maker internals, don't care
    battleback_name: str = attrs.field()
    battle_transition: str = attrs.field()
    start_x: int = attrs.field()
    start_y: int = attrs.field()
    windowskin_name: str = attrs.field()
    battler_hue: int = attrs.field()
    title_name: str = attrs.field()
    test_troop_id: int = attrs.field()
    gameover_name: str = attrs.field()
    # this should probably not be zero...
    start_map_id: int = attrs.field(default=1)
    edit_map_id: int = attrs.field(default=1)

    # whatever the hell these are
    words: RubyRpgWords = attrs.field()
    test_battlers: list[RubyRpgTestBattler] = attrs.field()
    party_members: list[int] = attrs.field()
    elements: list[str] = attrs.field()
    battler_name: str = attrs.field()

    @property
    @override
    def ruby_class_name(self) -> RubySymbol:
        return RPG_SYSTEM
