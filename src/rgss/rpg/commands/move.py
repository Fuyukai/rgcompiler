from __future__ import annotations

from typing import Any, override

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
        return {
            "command": "ToggleMoveAnimationCommand",
            "enable": self.enable
        }


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
        return {
            "command": "ToggleDirectionFixCommand",
            "enable": self.enable
        }
