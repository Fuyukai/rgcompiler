from __future__ import annotations

import enum
from typing import Any, Literal, NewType, cast, final, override

import attrs
from cattrs import Converter

from rgss.rpg.commands.base import RawCommand, RubyBaseEventCommand
from rhodochrosite.ruby import RubyMarshalValue


@attrs.define(kw_only=True)
class SetSwitchCommand(RubyBaseEventCommand):
    """
    An event command that sets one or more switches.
    """

    switch_start: int = attrs.field()
    switch_end: int = attrs.field()
    switch_value: bool = attrs.field()

    @classmethod
    @override
    def from_raw_command(cls, cmd: RawCommand) -> SetSwitchCommand:
        return SetSwitchCommand(
            switch_start=cast(int, cmd.parameters[0]),
            switch_end=cast(int, cmd.parameters[1]),
            # THIS IS CORRECT, FOR SOME STUPID FUCKING REASON IT'S INVERTED?
            switch_value=cmd.parameters[2] == 0,
            indent=cmd.indent,
        )

    @override
    def to_raw_command(self) -> RawCommand:
        return RawCommand(
            code=121,
            parameters=[self.switch_start, self.switch_end, int(not self.switch_value)],
            indent=self.indent,
        )

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {
            "command": "SetSwitchCommand",
            "switch_start": self.switch_start,
            "switch_end": self.switch_end,
            "switch_value": self.switch_value,
        }


@attrs.define(kw_only=True)
class SetSelfSwitchCommand(RubyBaseEventCommand):
    """
    An event command that sets a self-switch.
    """

    switch: Literal["A", "B", "C", "D"] = attrs.field()
    switch_value: bool = attrs.field()

    @classmethod
    @override
    def from_raw_command(cls, cmd: RawCommand) -> SetSelfSwitchCommand:
        return SetSelfSwitchCommand(
            switch=cast(Literal["A", "B", "C", "D"], cmd.parameters[0]),
            switch_value=cmd.parameters[1] == 0,
            indent=cmd.indent,
        )

    @override
    def to_raw_command(self) -> RawCommand:
        return RawCommand(
            code=123,
            parameters=[self.switch, int(not self.switch_value)],
            indent=self.indent,
        )

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {
            "command": "SetSelfSwitchCommand",
            "switch": self.switch,
            "switch_value": self.switch_value,
        }


# annoyingly, this is one of the few times i actually want rust-style enums!
# for Reborn purposes, Item/Actor/Enemy/Character can be completely ignored..


class SetVariableOpvalType(enum.IntEnum):
    Constant = 0
    Variable = 1
    Random = 2


SvOpvalConstant = NewType("SvOpvalConstant", int)
SvOpvalVariable = NewType("SvOpvalVariable", int)
SvOpvalRandom = NewType("SvOpvalRandom", tuple[int, int])

type SetVariableOpval = SvOpvalConstant | SvOpvalVariable | SvOpvalRandom


class SetVariableOpcode(enum.IntEnum):
    Set = 0
    Add = 1
    Sub = 2
    Mul = 3
    Div = 4
    Mod = 5


@attrs.define(kw_only=True)
@final
class SetVariableCommand(RubyBaseEventCommand):
    """
    An event command that sets a global variable.
    """

    variable_start: int = attrs.field()
    variable_end: int = attrs.field()

    opcode: SetVariableOpcode = attrs.field()

    opval_type: SetVariableOpvalType = attrs.field()
    opval: SetVariableOpval = attrs.field()

    @classmethod
    @override
    def from_raw_command(cls, cmd: RawCommand) -> SetVariableCommand:
        # fucking variable length format, ugh.
        opcode = SetVariableOpcode(cast(int, cmd.parameters[2]))
        opval_type = SetVariableOpvalType(cast(int, cmd.parameters[3]))

        opval: SetVariableOpval
        match opval_type:
            case SetVariableOpvalType.Constant:
                opval = SvOpvalConstant(cast(int, cmd.parameters[4]))

            case SetVariableOpvalType.Variable:
                opval = SvOpvalVariable(cast(int, cmd.parameters[4]))

            case SetVariableOpvalType.Random:
                lower = cast(int, cmd.parameters[4])
                upper = cast(int, cmd.parameters[5])
                opval = SvOpvalRandom((lower, upper))

        return SetVariableCommand(
            variable_start=cast(int, cmd.parameters[0]),
            variable_end=cast(int, cmd.parameters[1]),
            opcode=opcode,
            opval_type=opval_type,
            opval=opval,
            indent=cmd.indent,
        )

    @override
    def to_raw_command(self) -> RawCommand:
        parameters: list[RubyMarshalValue] = [
            self.variable_start,
            self.variable_end,
            self.opcode.value,
            self.opval_type.value,
        ]

        match self.opval_type:
            case SetVariableOpvalType.Constant | SetVariableOpvalType.Variable:
                parameters.append(int(self.opval))  # type: ignore

            case SetVariableOpvalType.Random:
                lower, upper = cast(SvOpvalRandom, self.opval)
                parameters.extend([lower, upper])

        return RawCommand(
            code=122,
            parameters=parameters,
            indent=self.indent,
        )

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {
            "command": "SetVariableCommand",
            "variable_start": self.variable_start,
            "variable_end": self.variable_end,
            "opcode": self.opcode.name,
            "opval_type": self.opval_type.name,
            "opval": self.opval,
        }
