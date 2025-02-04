from __future__ import annotations

import enum
from typing import Any, Literal, cast, final, override

import attrs
from cattrs import Converter

from rgss.rpg.commands.base import RawCommand, RubyBaseEventCommand
from rhodochrosite.ruby import RubyMarshalValue


@attrs.define(kw_only=True)
@final
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
        base: dict[str, Any] = {
            "command": "SetSwitchCommand",
            "switch_value": self.switch_value,
        }

        if self.switch_start == self.switch_end:
            base["switch"] = self.switch_start
        else:
            base["switch_start"] = self.switch_start
            base["switch_end"] = self.switch_end

        return base


@attrs.define(kw_only=True)
@final
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


# for Reborn purposes, Item/Actor/Enemy/Character can be completely ignored..


@attrs.define(kw_only=True, frozen=True)
@final
class SvOpvalConstant:
    __match_args__ = ("value",)

    value: int = attrs.field()


@attrs.define(kw_only=True, frozen=True)
@final
class SvOpvalVariable:
    __match_args__ = ("other_variable_id",)

    other_variable_id: int = attrs.field()


@attrs.define(kw_only=True, frozen=True)
class SvOpvalRandom:
    __match_args__ = ("lower", "upper")

    lower: int = attrs.field()
    upper: int = attrs.field()


class SvActorRefAttribute(enum.IntEnum):
    MapX = 0
    MapY = 1
    Direction = 2
    ScreenX = 3
    ScreenY = 4
    TerrainTag = 5


@attrs.define(kw_only=True, frozen=True)
class SvOpvalActorRefAttr:
    __match_args__ = ("actor_id", "attribute")

    actor_id: int = attrs.field()
    attribute: SvActorRefAttribute = attrs.field(converter=SvActorRefAttribute)


type SetVariableOpval = SvOpvalConstant | SvOpvalVariable | SvOpvalRandom | SvOpvalActorRefAttr


class SetVariableOpcode(enum.IntEnum):
    """
    The opcode for the set variable command.

    ``$v[start:end] = $v[start:end] OP opval``
    """

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
    opval: SetVariableOpval = attrs.field()

    @classmethod
    @override
    def from_raw_command(cls, cmd: RawCommand) -> SetVariableCommand:
        # fucking variable length format, ugh.
        opcode = SetVariableOpcode(cast(int, cmd.parameters[2]))

        match code := cast(int, cmd.parameters[3]):
            case 0:
                opval = SvOpvalConstant(value=cast(int, cmd.parameters[4]))

            case 1:
                opval = SvOpvalVariable(other_variable_id=cast(int, cmd.parameters[4]))

            case 2:
                lower = cast(int, cmd.parameters[4])
                upper = cast(int, cmd.parameters[5])
                opval = SvOpvalRandom(lower=lower, upper=upper)

            case 6:
                actor_id = cast(int, cmd.parameters[4])
                attribute = SvActorRefAttribute(cast(int, cmd.parameters[5]))
                opval = SvOpvalActorRefAttr(actor_id=actor_id, attribute=attribute)

            case _:
                raise NotImplementedError(
                    f"Unknown set variable opval {code} with params {cmd.parameters}"
                )

        return SetVariableCommand(
            variable_start=cast(int, cmd.parameters[0]),
            variable_end=cast(int, cmd.parameters[1]),
            opcode=opcode,
            opval=opval,
            indent=cmd.indent,
        )

    @override
    def to_raw_command(self) -> RawCommand:
        parameters: list[RubyMarshalValue] = [
            self.variable_start,
            self.variable_end,
            self.opcode.value,
        ]

        match self.opval:
            case SvOpvalConstant(value):
                parameters.append(0)
                parameters.append(value)

            case SvOpvalVariable(other_variable_id):
                parameters.append(1)
                parameters.append(other_variable_id)

            case SvOpvalRandom(lower, upper):
                parameters.append(2)
                parameters.append(lower)
                parameters.append(upper)

            case SvOpvalActorRefAttr(actor_id, attribute):
                parameters.append(6)
                parameters.append(actor_id)
                parameters.append(attribute.value)

        return RawCommand(
            code=122,
            parameters=parameters,
            indent=self.indent,
        )

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        base = {
            "command": "SetVariableCommand",
            "opcode": self.opcode.name,
            "opval": converter.unstructure(self.opval),
        }

        if self.variable_start == self.variable_end:
            base["variable"] = self.variable_start
        else:
            base["variable_start"] = self.variable_start
            base["variable_end"] = self.variable_end

        return base


@attrs.define(kw_only=True)
@final
class WaitForButtonPressCommand(RubyBaseEventCommand):
    """
    An event command that waits for a button press.
    """

    output_variable: int = attrs.field()

    @classmethod
    @override
    def from_raw_command(cls, cmd: RawCommand) -> WaitForButtonPressCommand:
        return WaitForButtonPressCommand(
            output_variable=cast(int, cmd.parameters[0]),
            indent=cmd.indent,
        )

    @override
    def to_raw_command(self) -> RawCommand:
        return RawCommand(
            code=105,
            parameters=[self.output_variable],
            indent=self.indent,
        )

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {
            "command": "WaitForButtonPressCommand",
            "output_variable": self.output_variable,
        }


@attrs.define(kw_only=True)
@final
class InputNumberCommand(RubyBaseEventCommand):
    """
    An event command that waits for a number input.
    """

    output_variable: int = attrs.field()

    @classmethod
    @override
    def from_raw_command(cls, cmd: RawCommand) -> InputNumberCommand:
        return InputNumberCommand(
            output_variable=cast(int, cmd.parameters[0]),
            indent=cmd.indent,
        )

    @override
    def to_raw_command(self) -> RawCommand:
        return RawCommand(
            code=103,
            parameters=[self.output_variable],
            indent=self.indent,
        )

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {
            "command": "InputNumberCommand",
            "output_variable": self.output_variable,
        }
