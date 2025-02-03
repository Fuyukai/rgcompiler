from __future__ import annotations

from typing import Any, cast, override

import attrs
from cattr import Converter

from rgss.rpg.commands.base import RawCommand, RubyBaseEventCommand
from rgss.rpg.misc import RubyAudioFile
from rgss.types import RgssColour, RgssDirection, RgssTone


@attrs.define(kw_only=True)
class ChangeScreenColourToneCommand(RubyBaseEventCommand):
    """
    An event command that changes the screen's colour tone.
    """

    tone: RgssTone = attrs.field()
    frames: int = attrs.field()

    @classmethod
    @override
    def from_raw_command(cls, cmd: RawCommand) -> ChangeScreenColourToneCommand:
        return ChangeScreenColourToneCommand(
            tone=cast(RgssTone, cmd.parameters[0]), frames=cast(int, cmd.parameters[1])
        )

    @override
    def to_raw_command(self) -> RawCommand:
        return RawCommand(code=223, parameters=[self.tone, self.frames])

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
    def from_raw_command(cls, cmd: RawCommand) -> ScreenFlashCommand:
        return ScreenFlashCommand(
            colour=cast(RgssTone, cmd.parameters[0]), frames=cast(int, cmd.parameters[1])
        )

    @override
    def to_raw_command(self) -> RawCommand:
        return RawCommand(code=224, parameters=[self.colour, self.frames])

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {
            "command": "ScreenFlashCommand",
            "colour": converter.unstructure(self.colour),
            "frames": self.frames,
        }


@attrs.define(kw_only=True)
class PlaySfxCommand(RubyBaseEventCommand):
    """
    An event command that plays a sound effect.
    """

    audio: RubyAudioFile = attrs.field()

    @classmethod
    @override
    def from_raw_command(cls, cmd: RawCommand) -> PlaySfxCommand:
        return PlaySfxCommand(audio=cast(RubyAudioFile, cmd.parameters[0]))

    @override
    def to_raw_command(self) -> RawCommand:
        return RawCommand(code=250, parameters=[self.audio])

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {
            "command": "PlaySfxCommand",
            "audio": converter.unstructure(self.audio),
        }


@attrs.define(kw_only=True)
class ScrollMapCommand(RubyBaseEventCommand):
    """
    An event command that scrolls the map.
    """

    direction: RgssDirection = attrs.field(converter=RgssDirection)
    distance: int = attrs.field()
    speed: int = attrs.field()

    @classmethod
    @override
    def from_raw_command(cls, cmd: RawCommand) -> ScrollMapCommand:
        return ScrollMapCommand(
            direction=cast(int, cmd.parameters[0]),
            distance=cast(int, cmd.parameters[1]),
            speed=cast(int, cmd.parameters[2]),
        )

    @override
    def to_raw_command(self) -> RawCommand:
        return RawCommand(code=204, parameters=[self.direction.value, self.distance, self.speed])

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {
            "command": "ScrollMapCommand",
            "direction": self.direction.name,
            "distance": self.distance,
            "speed": self.speed,
        }
