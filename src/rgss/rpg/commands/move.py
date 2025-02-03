from __future__ import annotations

from typing import Any, cast, override

import attrs
from cattrs import Converter

from rgss.rpg.commands.base import RawCommand, RubyBaseMoveCommand
from rgss.types import RgssDirection

DIRECTION_CODES = {
    RgssDirection.Down: 1,
    RgssDirection.Left: 2,
    RgssDirection.Right: 3,
    RgssDirection.Up: 4,
}
DIRECTION_REVERSE_CODES = [
    None,
    RgssDirection.Down,
    RgssDirection.Left,
    RgssDirection.Right,
    RgssDirection.Up,
]


# <MoveOnce direction="Left">
@attrs.define(kw_only=True)
class BasicDirectionMoveCommand(RubyBaseMoveCommand):
    """
    A move command for moving in one of the four cardinal directions.
    """

    direction: RgssDirection = attrs.field()

    @classmethod
    @override
    def from_raw_command(cls, cmd: RawCommand) -> BasicDirectionMoveCommand:
        direction = DIRECTION_REVERSE_CODES[cmd.code]
        assert direction, "wtf? don't put me in the dict under non 1-4"

        return cls(direction=direction)

    @override
    def to_raw_command(self) -> RawCommand:
        return RawCommand(code=DIRECTION_CODES[self.direction], parameters=[], indent=0)

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {"command": "BasicDirectionMoveCommand", "direction": self.direction.name}


@attrs.define(kw_only=True)
class CornerMoveCommand(RubyBaseMoveCommand):
    """
    A move command for moving an actor left/right and also upper/lower.
    """

    upper: bool = attrs.field()
    left: bool = attrs.field()

    @classmethod
    @override
    def from_raw_command(cls, cmd: RawCommand) -> CornerMoveCommand:
        match cmd.code:
            case 5:
                return CornerMoveCommand(upper=False, left=True)
            case 6:
                return CornerMoveCommand(upper=False, left=False)
            case 7:
                return CornerMoveCommand(upper=True, left=True)
            case 8:
                return CornerMoveCommand(upper=True, left=False)
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
            "command": "CornerMoveCommand",
            "upper": self.upper,
            "left": self.left,
        }


# <MoveStep backwards="true">
@attrs.define(kw_only=True)
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


@attrs.define(kw_only=True)
class ToggleMoveAnimationCommand(RubyBaseMoveCommand):
    """
    A move command for toggling enabling actor move animations.
    """

    enable: bool = attrs.field()

    @classmethod
    @override
    def from_raw_command(cls, cmd: RawCommand) -> ToggleMoveAnimationCommand:
        return cls(enable=cmd.code == 31)

    @override
    def to_raw_command(self) -> RawCommand:
        return RawCommand(code=31 if self.enable else 32, parameters=[], indent=0)

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {"command": "ToggleMoveAnimationCommand", "enable": self.enable}


@attrs.define(kw_only=True)
class ToggleDirectionFixCommand(RubyBaseMoveCommand):
    """
    A move command for toggling enabling actor direction fix (?).
    """

    enable: bool = attrs.field()

    @classmethod
    @override
    def from_raw_command(cls, cmd: RawCommand) -> ToggleDirectionFixCommand:
        return cls(enable=cmd.code == 35)

    @override
    def to_raw_command(self) -> RawCommand:
        return RawCommand(code=35 if self.enable else 36, parameters=[], indent=0)

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {"command": "ToggleDirectionFixCommand", "enable": self.enable}


@attrs.define(kw_only=True)
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
class WaitMoveCommand(RubyBaseMoveCommand):
    """
    A move command for waiting a certain number of frames.
    """

    frames: int = attrs.field()

    @classmethod
    @override
    def from_raw_command(cls, cmd: RawCommand) -> WaitMoveCommand:
        return cls(frames=cast(int, cmd.parameters[0]))

    @override
    def to_raw_command(self) -> RawCommand:
        return RawCommand(code=15, parameters=[self.frames], indent=0)

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {"command": "WaitMoveCommand", "frames": self.frames}
