from __future__ import annotations

from typing import Any, TypedDict, cast, override

import attrs
from cattr import Converter

from rgss.rpg.commands.base import RawEventCommand, RubyBaseEventCommand
from rgss.rpg.misc import RubyAudioFile
from rgss.types import RgssColour, RgssTone


@attrs.define(kw_only=True)
class ChangeScreenColourToneCommand(RubyBaseEventCommand):
    """
    An event command that changes the screen's colour tone.
    """

    tone: RgssTone = attrs.field()
    frames: int = attrs.field()

    @classmethod
    @override
    def from_raw_event_command(cls, cmd: RawEventCommand) -> ChangeScreenColourToneCommand:
        return ChangeScreenColourToneCommand(
            tone=cast(RgssTone, cmd.parameters[0]), frames=cast(int, cmd.parameters[1])
        )

    @override
    def get_raw_event_command(self) -> RawEventCommand:
        return RawEventCommand(code=223, parameters=[self.tone, self.frames])

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {
            "command": "ChangeScreenColourToneCommand",
            "tone": converter.unstructure(self.tone),
            "frames": self.frames,
        }


@attrs.define(kw_only=True)
class ScreenFlashCommand(RubyBaseEventCommand):
    """
    An event command that flashes the screen.
    """

    colour: RgssColour = attrs.field()
    frames: int = attrs.field()

    @classmethod
    @override
    def from_raw_event_command(cls, cmd: RawEventCommand) -> ScreenFlashCommand:
        return ScreenFlashCommand(
            colour=cast(RgssTone, cmd.parameters[0]), frames=cast(int, cmd.parameters[1])
        )

    @override
    def get_raw_event_command(self) -> RawEventCommand:
        return RawEventCommand(code=224, parameters=[self.colour, self.frames])

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {
            "command": "ScreenFlashCommand",
            "colour": converter.unstructure(self.colour),
            "frames": self.frames,
        }


class SfxTypedDict(TypedDict):
    name: str
    volume: int
    pitch: int


@attrs.define(kw_only=True)
class PlaySfxCommand(RubyBaseEventCommand):
    """
    An event command that plays a sound effect.
    """

    audio: RubyAudioFile = attrs.field()

    @classmethod
    @override
    def from_raw_event_command(cls, cmd: RawEventCommand) -> PlaySfxCommand:
        return PlaySfxCommand(audio=cast(RubyAudioFile, cmd.parameters[0]))

    @override
    def get_raw_event_command(self) -> RawEventCommand:
        return RawEventCommand(code=250, parameters=[self.audio])

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {
            "command": "PlaySfxCommand",
            "audio": converter.unstructure(self.audio),
        }
