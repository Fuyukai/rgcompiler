from __future__ import annotations

from typing import Any, cast, final, override

import attrs
from cattrs import Converter

from rgss.rpg.commands.base import (
    RPG_EVENT_COMMAND,
    RawCommand,
    RubyBaseCommand,
    RubyBaseEventCommand,
)
from rgss.rpg.misc import RubyAudioFile
from rgss.types import RgssColour, RgssDirection, RgssTone
from rhodochrosite.ruby import RubySymbol


@attrs.define(kw_only=True)
@final
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
            tone=cast(RgssTone, cmd.parameters[0]),
            frames=cast(int, cmd.parameters[1]),
            indent=cmd.indent,
        )

    @override
    def to_raw_command(self) -> RawCommand:
        return RawCommand(code=223, parameters=[self.tone, self.frames], indent=self.indent)

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {
            "command": "ChangeScreenColourToneCommand",
            "tone": converter.unstructure(self.tone),
            "frames": self.frames,
        }


@attrs.define(kw_only=True)
@final
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
            colour=cast(RgssTone, cmd.parameters[0]),
            frames=cast(int, cmd.parameters[1]),
            indent=cmd.indent,
        )

    @override
    def to_raw_command(self) -> RawCommand:
        return RawCommand(code=224, parameters=[self.colour, self.frames], indent=self.indent)

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {
            "command": "ScreenFlashCommand",
            "colour": converter.unstructure(self.colour),
            "frames": self.frames,
        }


@attrs.define(kw_only=True)
@final
class PlaySfxCommand(RubyBaseCommand):
    """
    A command that plays a sound effect.

    This is shared between event and move commands.
    """

    type: RubySymbol = attrs.field()
    audio: RubyAudioFile = attrs.field()
    indent: int = attrs.field()

    @classmethod
    @override
    def from_raw_command_and_type(cls, type: RubySymbol, cmd: RawCommand) -> PlaySfxCommand:
        return PlaySfxCommand(
            type=type, audio=cast(RubyAudioFile, cmd.parameters[0]), indent=cmd.indent
        )

    @property
    @override
    def ruby_class_name(self) -> RubySymbol:
        return self.type

    @override
    def to_raw_command(self) -> RawCommand:
        code = 250 if self.type == RPG_EVENT_COMMAND else 44
        return RawCommand(code=code, parameters=[self.audio], indent=self.indent)

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {
            "command": "PlaySfxCommand",
            "audio": converter.unstructure(self.audio),
        }


@attrs.define(kw_only=True)
@final
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
            indent=cmd.indent,
        )

    @override
    def to_raw_command(self) -> RawCommand:
        return RawCommand(
            code=203,
            parameters=[self.direction.value, self.distance, self.speed],
            indent=self.indent,
        )

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {
            "command": "ScrollMapCommand",
            "direction": self.direction.name,
            "distance": self.distance,
            "speed": self.speed,
        }


@attrs.define(kw_only=True)
@final
class FadeOutBgmCommand(RubyBaseEventCommand):
    """
    Event command that fades out the BGM.
    """

    # in seconds, not frames?
    fade_time: int = attrs.field()

    @classmethod
    @override
    def from_raw_command(cls, cmd: RawCommand) -> FadeOutBgmCommand:
        return FadeOutBgmCommand(
            fade_time=cast(int, cmd.parameters[0]),
            indent=cmd.indent,
        )

    @override
    def to_raw_command(self) -> RawCommand:
        return RawCommand(
            code=242,
            parameters=[self.fade_time],
            indent=self.indent,
        )

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {
            "command": "FadeOutBgmCommand",
            "fade_time": self.fade_time,
        }


@attrs.define(kw_only=True)
@final
class PlayBgmCommand(RubyBaseEventCommand):
    """
    Event command that starts playing music.
    """

    audio: RubyAudioFile = attrs.field()
    #: If True, this is an "ME", which temporarily replaces the BGM.
    #:
    #: What does "ME" stand for? Who fucking knows.
    is_me: bool = attrs.field()

    @classmethod
    @override
    def from_raw_command(cls, cmd: RawCommand) -> PlayBgmCommand:
        is_me = cmd.code == 249
        return PlayBgmCommand(
            audio=cast(RubyAudioFile, cmd.parameters[0]),
            indent=cmd.indent,
            is_me=is_me,
        )

    @override
    def to_raw_command(self) -> RawCommand:
        code = 249 if self.is_me else 241

        return RawCommand(
            code=code,
            parameters=[self.audio],
            indent=self.indent,
        )

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {
            "command": "PlayBgmCommand",
            "audio": converter.unstructure(self.audio),
            "is_me": self.is_me,
        }


@attrs.define(kw_only=True)
@final
class ChangeBattleBgmCommand(RubyBaseEventCommand):
    """
    Changes the battle BGM.
    """

    audio: RubyAudioFile = attrs.field()

    @classmethod
    @override
    def from_raw_command(cls, cmd: RawCommand) -> ChangeBattleBgmCommand:
        return ChangeBattleBgmCommand(
            audio=cast(RubyAudioFile, cmd.parameters[0]),
            indent=cmd.indent,
        )

    @override
    def to_raw_command(self) -> RawCommand:
        return RawCommand(
            code=132,
            parameters=[self.audio],
            indent=self.indent,
        )

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {
            "command": "ChangeBattleBgmCommand",
            "audio": converter.unstructure(self.audio),
        }


@attrs.define(kw_only=True)
@final
class ShowAnimationCommand(RubyBaseEventCommand):
    """
    An event command that shows an animation.
    """

    target: int = attrs.field()
    animation_id: int = attrs.field()

    @classmethod
    @override
    def from_raw_command(cls, cmd: RawCommand) -> ShowAnimationCommand:
        return ShowAnimationCommand(
            target=cast(int, cmd.parameters[0]),
            animation_id=cast(int, cmd.parameters[1]),
            indent=cmd.indent,
        )

    @override
    def to_raw_command(self) -> RawCommand:
        return RawCommand(
            code=207,
            parameters=[self.target, self.animation_id],
            indent=self.indent,
        )

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {
            "command": "ShowAnimationCommand",
            "target": self.target,
            "animation_id": self.animation_id,
        }


@attrs.define(kw_only=True)
@final
class ScreenShakeCommand(RubyBaseEventCommand):
    """
    An event command that shakes the screen.
    """

    power: int = attrs.field()
    speed: int = attrs.field()
    frames: int = attrs.field()

    @classmethod
    @override
    def from_raw_command(cls, cmd: RawCommand) -> ScreenShakeCommand:
        return ScreenShakeCommand(
            power=cast(int, cmd.parameters[0]),
            speed=cast(int, cmd.parameters[1]),
            frames=cast(int, cmd.parameters[2]),
            indent=cmd.indent,
        )

    @override
    def to_raw_command(self) -> RawCommand:
        return RawCommand(
            code=225,
            parameters=[self.power, self.speed, self.frames],
            indent=self.indent,
        )

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {
            "command": "ScreenShakeCommand",
            "power": self.power,
            "speed": self.speed,
            "frames": self.frames,
        }


@attrs.define(kw_only=True)
@final
class SetTransparencyFlagCommand(RubyBaseEventCommand):
    """
    Sets the transparency flag for this event.
    """

    # i.e. not transparent!
    normal: bool = attrs.field()

    @classmethod
    @override
    def from_raw_command(cls, cmd: RawCommand) -> SetTransparencyFlagCommand:
        # wow, the first rgss event that ISN'T fucking inverted
        return SetTransparencyFlagCommand(
            normal=cast(bool, cmd.parameters[0]),
            indent=cmd.indent,
        )

    @override
    def to_raw_command(self) -> RawCommand:
        return RawCommand(
            code=208,
            parameters=[self.normal],
            indent=self.indent,
        )

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {
            "command": "SetTransparencyFlagCommand",
            "flag": self.normal,
        }


@attrs.define(kw_only=True)
@final
class ChangeFogOpacityCommand(RubyBaseEventCommand):
    """
    Changes the fog's opacity.
    """

    opacity: int = attrs.field()
    frames: int = attrs.field()

    @classmethod
    @override
    def from_raw_command(cls, cmd: RawCommand) -> ChangeFogOpacityCommand:
        return ChangeFogOpacityCommand(
            opacity=cast(int, cmd.parameters[0]),
            frames=cast(int, cmd.parameters[1]),
            indent=cmd.indent,
        )

    @override
    def to_raw_command(self) -> RawCommand:
        return RawCommand(
            code=206,
            parameters=[self.opacity, self.frames],
            indent=self.indent,
        )

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {
            "command": "ChangeFogOpacityCommand",
            "opacity": self.opacity,
            "frames": self.frames,
        }
