from __future__ import annotations

import enum
from typing import Any, cast, final, override

import attrs
from cattrs import Converter

from rgss.rpg.commands.base import RawCommand, RubyBaseMoveCommand
from rgss.types import HasGraphicProperties, RgssDirection

DIRECTION_CODES = {
    RgssDirection.Down: 1,
    RgssDirection.Left: 2,
    RgssDirection.Right: 3,
    RgssDirection.Up: 4,
}
DIRECTION_REVERSE_CODES = [
    RgssDirection.Down,
    RgssDirection.Left,
    RgssDirection.Right,
    RgssDirection.Up,
]


# <MoveOnce direction="Left">
@attrs.define(kw_only=True)
@final
class CardinalMoveCommand(RubyBaseMoveCommand):
    """
    A move command for moving in one of the four cardinal directions.
    """

    direction: RgssDirection = attrs.field()

    @classmethod
    @override
    def from_raw_command(cls, cmd: RawCommand) -> CardinalMoveCommand:
        direction = DIRECTION_REVERSE_CODES[cmd.code - 1]
        assert direction, "wtf? don't put me in the dict under non 1-4"

        return cls(direction=direction)

    @override
    def to_raw_command(self) -> RawCommand:
        return RawCommand(code=DIRECTION_CODES[self.direction], parameters=[], indent=0)

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {"command": "CardinalMoveCommand", "direction": self.direction.name}


@attrs.define(kw_only=True)
@final
class DiagonalMoveCommand(RubyBaseMoveCommand):
    """
    A move command for moving an actor left/right and also upper/lower.
    """

    upper: bool = attrs.field()
    left: bool = attrs.field()

    @classmethod
    @override
    def from_raw_command(cls, cmd: RawCommand) -> DiagonalMoveCommand:
        match cmd.code:
            case 5:
                return DiagonalMoveCommand(upper=False, left=True)
            case 6:
                return DiagonalMoveCommand(upper=False, left=False)
            case 7:
                return DiagonalMoveCommand(upper=True, left=True)
            case 8:
                return DiagonalMoveCommand(upper=True, left=False)
            case _:
                raise ValueError(f"Invalid corner move command code: {cmd.code}")

    @override
    def to_raw_command(self) -> RawCommand:
        code: int
        if self.upper and self.left:
            code = 7
        elif self.upper and not self.left:
            code = 8
        elif not self.upper and self.left:
            code = 5
        else:
            code = 6

        return RawCommand(code=code, parameters=[], indent=0)

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {
            "command": "DiagonalMoveCommand",
            "upper": self.upper,
            "left": self.left,
        }


# <MoveStep backwards="true">
@attrs.define(kw_only=True)
@final
class StepOneCommand(RubyBaseMoveCommand):
    """
    A move command for stepping forwards or backwards.
    """

    backwards: bool = attrs.field()

    @classmethod
    @override
    def from_raw_command(cls, cmd: RawCommand) -> StepOneCommand:
        return cls(backwards=cmd.code == 13)

    @override
    def to_raw_command(self) -> RawCommand:
        return RawCommand(code=13 if self.backwards else 12, parameters=[], indent=0)

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {
            "command": "StepOneCommand",
            "direction": "Backwards" if self.backwards else "Forwards",
        }


@final
class ToggleCommandProperty(enum.Enum):
    MoveAnimation = 0
    DirectionFix = 1
    Collision = 2
    AlwaysOnTop = 3
    StopAnimation = 4


@attrs.define(kw_only=True)
@final
class TogglePropertyMoveCommand(RubyBaseMoveCommand):
    """
    A move command for toggling various properties of an actor.
    """

    prop: ToggleCommandProperty = attrs.field()
    toggle: bool = attrs.field()

    @classmethod
    @override
    def from_raw_command(cls, cmd: RawCommand) -> TogglePropertyMoveCommand:
        prop: ToggleCommandProperty
        if cmd.code == 31 or cmd.code == 32:
            prop = ToggleCommandProperty.MoveAnimation
        elif cmd.code == 33 or cmd.code == 34:
            prop = ToggleCommandProperty.StopAnimation
        elif cmd.code == 35 or cmd.code == 36:
            prop = ToggleCommandProperty.DirectionFix
        elif cmd.code == 37 or cmd.code == 38:
            prop = ToggleCommandProperty.Collision
        elif cmd.code == 39 or cmd.code == 40:
            prop = ToggleCommandProperty.AlwaysOnTop
        else:
            raise ValueError(f"Invalid toggle property command code: {cmd.code}")

        return cls(prop=prop, toggle=cmd.code % 2 == 1)

    @override
    def to_raw_command(self) -> RawCommand:
        code: int
        if self.prop == ToggleCommandProperty.MoveAnimation:
            code = 31 if self.toggle else 32
        elif self.prop == ToggleCommandProperty.StopAnimation:
            code = 33 if self.toggle else 34
        elif self.prop == ToggleCommandProperty.DirectionFix:
            code = 35 if self.toggle else 36
        elif self.prop == ToggleCommandProperty.Collision:
            code = 37 if self.toggle else 38
        elif self.prop == ToggleCommandProperty.AlwaysOnTop:
            code = 39 if self.toggle else 40
        else:
            raise ValueError(f"Invalid toggle property command property: {self.prop}")

        return RawCommand(code=code, parameters=[], indent=0)

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {
            "command": "TogglePropertyMoveCommand",
            "property": self.prop.name,
            "toggle": self.toggle,
        }


@attrs.define(kw_only=True)
@final
class ChangeSpeedCommand(RubyBaseMoveCommand):
    """
    A move command for changing the speed of subsequent commands.
    """

    speed: int = attrs.field()

    @classmethod
    @override
    def from_raw_command(cls, cmd: RawCommand) -> ChangeSpeedCommand:
        return cls(speed=cast(int, cmd.parameters[0]))

    @override
    def to_raw_command(self) -> RawCommand:
        return RawCommand(code=29, parameters=[self.speed], indent=0)

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {"command": "ChangeSpeedCommand", "speed": self.speed}


@attrs.define(kw_only=True)
@final
class TurnAbsoluteCommand(RubyBaseMoveCommand):
    """
    A move command for moving in one of the four cardinal directions.
    """

    direction: RgssDirection = attrs.field()

    @classmethod
    @override
    def from_raw_command(cls, cmd: RawCommand) -> TurnAbsoluteCommand:
        direction = DIRECTION_REVERSE_CODES[cmd.code - 16]
        assert direction, "wtf? don't put me in the dict under the wrong code!"

        return cls(direction=direction)

    @override
    def to_raw_command(self) -> RawCommand:
        return RawCommand(code=DIRECTION_CODES[self.direction] + 15, parameters=[], indent=0)

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {"command": "TurnAbsoluteCommand", "direction": self.direction.name}


@attrs.define(kw_only=True)
@final
class SetGraphicMoveCommand(RubyBaseMoveCommand, HasGraphicProperties):
    """
    A move command for setting the graphic of the event.
    """

    character_name: str = attrs.field()
    character_hue: int = attrs.field()
    direction: RgssDirection = attrs.field()
    pattern: int = attrs.field()

    @classmethod
    @override
    def from_raw_command(cls, cmd: RawCommand) -> SetGraphicMoveCommand:
        return cls(
            character_name=cast(str, cmd.parameters[0]),
            character_hue=cast(int, cmd.parameters[1]),
            direction=RgssDirection(cast(int, cmd.parameters[2])),
            pattern=cast(int, cmd.parameters[3]),
        )

    @override
    def to_raw_command(self) -> RawCommand:
        return RawCommand(
            code=41,
            parameters=[
                self.character_name,
                self.character_hue,
                self.direction.value,
                self.pattern,
            ],
            indent=0,
        )

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {
            "command": "SetGraphicMoveCommand",
            "character_name": self.character_name,
            "hue": self.character_hue,
            "direction": self.direction.name,
            "pattern": self.pattern,
        }


@attrs.define(kw_only=True)
@final
class FaceRelativeToPlayerCommand(RubyBaseMoveCommand):
    """
    A move command for turning towards or away from the player.
    """

    towards: bool = attrs.field()

    @classmethod
    @override
    def from_raw_command(cls, cmd: RawCommand) -> FaceRelativeToPlayerCommand:
        towards: bool
        if cmd.code == 25:
            towards = True
        elif cmd.code == 26:
            towards = False
        else:
            raise ValueError(f"code {cmd.code} ain't valid for a turn relative to player")

        return cls(towards=towards)

    @override
    def to_raw_command(self) -> RawCommand:
        return RawCommand(code=25, parameters=[], indent=0)

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {"command": "FaceRelativeToPlayerCommand", "towards": self.towards}


@attrs.define(kw_only=True)
@final
class JumpMoveCommand(RubyBaseMoveCommand):
    """
    A move command for jumping.
    """

    # Update: It's relative!

    x: int = attrs.field()
    y: int = attrs.field()

    @classmethod
    @override
    def from_raw_command(cls, cmd: RawCommand) -> JumpMoveCommand:
        return cls(x=cast(int, cmd.parameters[0]), y=cast(int, cmd.parameters[1]))

    @override
    def to_raw_command(self) -> RawCommand:
        return RawCommand(code=14, parameters=[self.x, self.y], indent=0)

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {"command": "JumpMoveCommand", "x": self.x, "y": self.y}


@attrs.define(kw_only=True)
@final
class TurnRandomlyCommand(RubyBaseMoveCommand):
    """
    A move command that turns the actor in a random direction.
    """

    @classmethod
    @override
    def from_raw_command(cls, cmd: RawCommand) -> TurnRandomlyCommand:
        return cls()

    @override
    def to_raw_command(self) -> RawCommand:
        return RawCommand(code=24, parameters=[], indent=0)

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {"command": "TurnRandomlyCommand"}


@attrs.define(kw_only=True)
@final
class SetOpacityCommand(RubyBaseMoveCommand):
    """
    A move command that sets the opacity of the actor.
    """

    # between 0 and 255?
    opacity: int = attrs.field()

    @classmethod
    @override
    def from_raw_command(cls, cmd: RawCommand) -> SetOpacityCommand:
        return cls(opacity=cast(int, cmd.parameters[0]))

    @override
    def to_raw_command(self) -> RawCommand:
        return RawCommand(code=42, parameters=[self.opacity], indent=0)

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {"command": "SetOpacityCommand", "opacity": self.opacity}
