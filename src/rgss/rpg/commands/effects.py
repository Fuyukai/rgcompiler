from __future__ import annotations

import enum
from typing import Any, assert_never, cast, final, override

import attrs
from cattrs import Converter

from rgss.rpg.commands.base import (
    RPG_EVENT_COMMAND,
    ConstantCoords,
    LoadVariableCoords,
    RawCommand,
    RubyBaseCommand,
    RubyBaseEventCommand,
)
from rgss.rpg.misc import RubyAudioFile
from rgss.types import RgssColour, RgssDirection, RgssTone
from rhodochrosite.ruby import RubyMarshalValue, RubySymbol


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
class StopSfxCommand(RubyBaseEventCommand):
    """
    Stops the currently playing sound effect.
    """

    @classmethod
    @override
    def from_raw_command(cls, cmd: RawCommand) -> StopSfxCommand:
        return StopSfxCommand(indent=cmd.indent)

    @override
    def to_raw_command(self) -> RawCommand:
        return RawCommand(code=251, parameters=[], indent=self.indent)

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {
            "command": "StopSfxCommand",
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


@final
class BackgroundSoundType(enum.Enum):
    BGM = 1
    BGS = 2
    ME = 3

    @classmethod
    def from_raw_event_code(cls, code: int) -> BackgroundSoundType:
        """
        Gets a new background sound type from the raw event code.
        """

        if code == 241 or code == 242:
            return BackgroundSoundType.BGM

        if code == 245 or code == 246:
            return cls.BGS

        if code == 249:
            return cls.ME

        raise ValueError(f"Invalid background sound code: {code}")

    def as_raw_event_code(self, fade_out: bool) -> int:
        """
        Converts this enum into a raw event code.
        """

        if self == BackgroundSoundType.BGM:
            return 242 if fade_out else 241

        if self == BackgroundSoundType.BGS:
            return 246 if fade_out else 245

        if self == BackgroundSoundType.ME:
            return 249

        assert_never(self)


@attrs.define(kw_only=True)
@final
class PlayBackgroundAudioCommand(RubyBaseEventCommand):
    """
    Event command that plays some form of background audio.
    """

    audio: RubyAudioFile = attrs.field()
    type: BackgroundSoundType = attrs.field()

    @classmethod
    @override
    def from_raw_command(cls, cmd: RawCommand) -> PlayBackgroundAudioCommand:
        typecode = BackgroundSoundType.from_raw_event_code(cmd.code)

        return PlayBackgroundAudioCommand(
            type=typecode,
            audio=cast(RubyAudioFile, cmd.parameters[0]),
            indent=cmd.indent,
        )

    @override
    def to_raw_command(self) -> RawCommand:
        return RawCommand(
            code=self.type.as_raw_event_code(fade_out=False),
            parameters=[self.audio],
            indent=self.indent,
        )

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        name: str = f"Play{self.type.name.capitalize()}Command"

        return {
            "command": name,
            "audio": converter.unstructure(self.audio),
        }


@attrs.define(kw_only=True)
@final
class FadeOutBackgroundAudioCommand(RubyBaseEventCommand):
    """
    Event command that fades out some form of background audio.
    """

    # in seconds, not frames?
    fade_time: int = attrs.field()

    type: BackgroundSoundType = attrs.field()

    @classmethod
    @override
    def from_raw_command(cls, cmd: RawCommand) -> FadeOutBackgroundAudioCommand:
        type = BackgroundSoundType.from_raw_event_code(cmd.code)

        return FadeOutBackgroundAudioCommand(
            type=type,
            fade_time=cast(int, cmd.parameters[0]),
            indent=cmd.indent,
        )

    @override
    def to_raw_command(self) -> RawCommand:
        return RawCommand(
            code=self.type.as_raw_event_code(fade_out=True),
            parameters=[self.fade_time],
            indent=self.indent,
        )

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        name: str = f"FadeOut{self.type.name.capitalize()}Command"

        return {
            "command": name,
            "fade_time": self.fade_time,
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


class ShowPictureOrigin(enum.Enum):
    """
    The origin of the picture.
    """

    UPPER_LEFT = 0
    CENTER = 1


@attrs.define(kw_only=True)
@final
class PictureEffectData:
    """
    Contains shared fields for how a picture is rendered.
    """

    origin: ShowPictureOrigin = attrs.field(default=ShowPictureOrigin.UPPER_LEFT)

    # relative to origin selection
    coords: ConstantCoords | LoadVariableCoords = attrs.field(default=ConstantCoords(x=0, y=0))
    zoom_x: int = attrs.field(default=100)
    zoom_y: int = attrs.field(default=100)
    opacity: int = attrs.field(default=255)
    blend_type: int = attrs.field(default=0)

    @classmethod
    def from_ruby_params(cls, params: list[RubyMarshalValue]) -> PictureEffectData:
        origin = ShowPictureOrigin(params[0])
        x = cast(int, params[2])
        y = cast(int, params[3])

        uses_variables = params[1] == 1

        if uses_variables:
            coords = LoadVariableCoords(x_variable=x, y_variable=y)
        else:
            coords = ConstantCoords(x=x, y=y)

        return PictureEffectData(
            origin=origin,
            coords=coords,
            zoom_x=cast(int, params[4]),
            zoom_y=cast(int, params[5]),
            opacity=cast(int, params[6]),
            blend_type=cast(int, params[7]),
        )


@attrs.define(kw_only=True)
@final
class ShowPictureCommand(RubyBaseEventCommand):
    """
    Shows a picture on the screen.
    """

    # matched with an erase command
    picture_id: int = attrs.field()
    filename: str = attrs.field()
    inner: PictureEffectData = attrs.field()

    @classmethod
    @override
    def from_raw_command(cls, cmd: RawCommand) -> ShowPictureCommand:
        inner = PictureEffectData.from_ruby_params(cmd.parameters[2:])
        return ShowPictureCommand(
            picture_id=cast(int, cmd.parameters[0]),
            filename=cast(str, cmd.parameters[1]),
            inner=inner,
            indent=cmd.indent,
        )

    @override
    def to_raw_command(self) -> RawCommand:
        params: list[RubyMarshalValue] = [self.picture_id, self.filename, self.inner.origin.value]

        if isinstance(self.inner.coords, ConstantCoords):
            params.extend([0, self.inner.coords.x, self.inner.coords.y])
        else:
            params.extend([1, self.inner.coords.x_variable, self.inner.coords.y_variable])

        params.extend([
            self.inner.zoom_x,
            self.inner.zoom_y,
            self.inner.opacity,
            self.inner.blend_type,
        ])
        return RawCommand(code=231, parameters=params, indent=self.indent)

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {
            "command": "ShowPictureCommand",
            "picture_id": self.picture_id,
            "filename": self.filename,
            "inner": converter.unstructure(self.inner),
        }


@attrs.define(kw_only=True)
@final
class ErasePictureCommand(RubyBaseEventCommand):
    """
    Erases a picture from the screen.
    """

    picture_id: int = attrs.field()

    @classmethod
    @override
    def from_raw_command(cls, cmd: RawCommand) -> ErasePictureCommand:
        return ErasePictureCommand(
            picture_id=cast(int, cmd.parameters[0]),
            indent=cmd.indent,
        )

    @override
    def to_raw_command(self) -> RawCommand:
        return RawCommand(code=235, parameters=[self.picture_id], indent=self.indent)

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {
            "command": "ErasePictureCommand",
            "picture_id": self.picture_id,
        }


@attrs.define(kw_only=True)
@final
class AlterPictureCommand(RubyBaseEventCommand):
    """
    Moves or alters a picture on the screen.
    """

    # in the editor, this is "Move Picture", but you can just not move it and do things like adjust
    # zoom and opacity for fade-ins or fade-outs.

    picture_id: int = attrs.field()
    frames: int = attrs.field()
    inner: PictureEffectData = attrs.field()

    @classmethod
    @override
    def from_raw_command(cls, cmd: RawCommand) -> AlterPictureCommand:
        frames = cast(int, cmd.parameters[1])
        inner = PictureEffectData.from_ruby_params(cmd.parameters[2:])
        return AlterPictureCommand(
            picture_id=cast(int, cmd.parameters[0]),
            frames=frames,
            inner=inner,
            indent=cmd.indent,
        )

    @override
    def to_raw_command(self) -> RawCommand:
        params: list[RubyMarshalValue] = [self.picture_id, self.frames, self.inner.origin.value]

        if isinstance(self.inner.coords, ConstantCoords):
            params.extend([0, self.inner.coords.x, self.inner.coords.y])
        else:
            params.extend([1, self.inner.coords.x_variable, self.inner.coords.y_variable])

        params.extend([
            self.inner.zoom_x,
            self.inner.zoom_y,
            self.inner.opacity,
            self.inner.blend_type,
        ])
        return RawCommand(code=232, parameters=params, indent=self.indent)

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {
            "command": "AlterPictureCommand",
            "picture_id": self.picture_id,
            "inner": converter.unstructure(self.inner),
        }


@attrs.define(kw_only=True)
@final
class RotatePictureCommand(RubyBaseEventCommand):
    """
    Rotates a picture on the screen.
    """

    picture_id: int = attrs.field()
    # ? what is this
    speed: int = attrs.field()

    @classmethod
    @override
    def from_raw_command(cls, cmd: RawCommand) -> RotatePictureCommand:
        return RotatePictureCommand(
            picture_id=cast(int, cmd.parameters[0]),
            speed=cast(int, cmd.parameters[1]),
            indent=cmd.indent,
        )

    @override
    def to_raw_command(self) -> RawCommand:
        return RawCommand(code=233, parameters=[self.picture_id, self.speed], indent=self.indent)

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {
            "command": "RotatePictureCommand",
            "picture_id": self.picture_id,
            "speed": self.speed,
        }


@final
class WeatherEffectType(enum.Enum):
    Clear = 0
    Rain = 1
    Storm = 2
    Snow = 3


@attrs.define(kw_only=True)
@final
class SetWeatherEffectsCommand(RubyBaseEventCommand):
    """
    Sets weather effects on the screen.
    """

    type: WeatherEffectType = attrs.field()
    strength: int = attrs.field()
    frames: int = attrs.field()

    @classmethod
    @override
    def from_raw_command(cls, cmd: RawCommand) -> SetWeatherEffectsCommand:
        return SetWeatherEffectsCommand(
            type=WeatherEffectType(cmd.parameters[0]),
            strength=cast(int, cmd.parameters[1]),
            frames=cast(int, cmd.parameters[2]),
            indent=cmd.indent,
        )

    @override
    def to_raw_command(self) -> RawCommand:
        return RawCommand(
            code=236,
            parameters=[self.type.value, self.strength, self.frames],
            indent=self.indent,
        )

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {
            "command": "SetWeatherEffectsCommand",
            "type": self.type.name,
            "strength": self.strength,
            "frames": self.frames,
        }
