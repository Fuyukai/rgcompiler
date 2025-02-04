from __future__ import annotations

import enum
from typing import Any, Literal, cast, final, override

import attrs
from cattrs import Converter

from rgss.rpg.commands.base import RawCommand, RubyBaseEventCommand
from rgss.types import RgssDirection
from rhodochrosite.ruby import RubyMarshalValue

# Branch instructions are a bit weird. In typical bytecode and machine code, branches are
# implemented using a compare -> jump pair. For example, in 32-bit ARM, this:
#
#    if (condition == 1) {
#        do_something();
#    } else {
#        do_something_else();
#    }
#
# Would be compiled into this:
#
# fn:
#        cmp     r0, #1
#        push    {r4, lr}
#        bne     .L2
#        bl      do_something
# .L1:
#        pop     {r4, lr}
#        bx      lr
# .L2:
#        bl      do_something_else
#        b       .L1
#
# Whilst the control flow is a bit messy for non-asm programmers, you can see that it compares
# the value and then *branches* to the else block if it doesn't match.
#
# This is not the case for RPG Maker events; it is far stupider (at least the MKXP-Z impl). Here
# is how a typical branch setup is laid out:
#
# Conditional Branch: <condition>
#   Op1
#   Op2
# Else
#   Op3
#   Op4
# End
#
# As best as I can tell, this system works on the following rules:
#
# 1) Evaluate the condition. If True, move to 2a. If False, move to 2b.
# 2a) Increment the acceptable indentation and continue instructions.
# 2b) Do nothing and continue instructions.
# 3) When hitting an Else, check the previous condition evaluation. If it was True, move to 4a.
#    If it was False, move to 4b.
# 4a) Do nothing and continue instructions.
# 4b) Increment the acceptable indentation and continue instructions.
# 5) When hitting an End, set the acceptable indentation to the indentation of the End instruction.
#
# Every instruction has an "indent" which shows up in the event editor. I believed this was purely
# cosmetic, but after stripping them I realised there is a hidden "acceptable indentation" variable
# that the interpreter uses to determine if commands should be executed or not. If Rhodochrosite
# is used to manually place things between the Conditional Branch and Else commands with an
# incorrect indentation, those commands will *always* be executed regardless of if the condition
# evaluates true.


@attrs.define(kw_only=True)
class ElseCommand(RubyBaseEventCommand):
    """
    An event command that is the "else" part of a conditional branch.
    """

    indent: int = attrs.field(default=0)

    @classmethod
    @override
    def from_raw_command(cls, cmd: RawCommand) -> ElseCommand:
        return ElseCommand(indent=cmd.indent)

    @override
    def to_raw_command(self) -> RawCommand:
        return RawCommand(code=411, indent=self.indent)

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {"command": "ElseCommand"}


@attrs.define(kw_only=True)
class EndBranchCommand(RubyBaseEventCommand):
    """
    An event command that ends a conditional branch.
    """

    indent: int = attrs.field(default=0)

    @classmethod
    @override
    def from_raw_command(cls, cmd: RawCommand) -> EndBranchCommand:
        return EndBranchCommand(indent=cmd.indent)

    @override
    def to_raw_command(self) -> RawCommand:
        return RawCommand(code=412, indent=self.indent)

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {"command": "EndBranchCommand"}


@attrs.define(kw_only=True, frozen=True)
class CheckSwitchOpval:
    """
    Branch opval for checking if a switch is set or not.

    This is also used for self switches.
    """

    switch_id: int | Literal["A", "B", "C", "D"] = attrs.field()
    is_on: bool = attrs.field()


class CompareVariableOpcode(enum.Enum):
    Equal = 0
    GreaterThanEqual = 1
    LessThanEqual = 2
    GreaterThan = 3
    LessThan = 4
    NotEqual = 5


@attrs.define(kw_only=True, frozen=True)
class CompareVariableToConstantOpval:
    """
    Branch opval for comparing a variable to a constant.
    """

    variable_id: int = attrs.field()
    opcode: CompareVariableOpcode = attrs.field()
    constant: int = attrs.field()


@attrs.define(kw_only=True, frozen=True)
class CompareVariableToVariableOpval:
    """
    Branch opval for comparing a variable to another variable.
    """

    variable_id: int = attrs.field()
    opcode: CompareVariableOpcode = attrs.field()
    other_variable_id: int = attrs.field()


@attrs.define(kw_only=True, frozen=True)
class CheckFacingOpval:
    """
    Branch opval for checking if an RPG Maker "character" is facing a direction.
    """

    # 0 = this event, -1 = player
    character_id: int = attrs.field()
    direction: RgssDirection = attrs.field()


@attrs.define(kw_only=True, frozen=True)
class CheckScriptReturnOpval:
    """
    Branch opval for checking if a bit of Ruby code returns true.
    """

    script: str = attrs.field()


type ComparisonOpvals = (
    CheckSwitchOpval
    | CompareVariableToConstantOpval
    | CompareVariableToVariableOpval
    | CheckFacingOpval
    | CheckScriptReturnOpval
)


@attrs.define(kw_only=True)
@final
class ConditionalBranchCommand(RubyBaseEventCommand):
    """
    An event command that only processes subsequent commands if a condition evaluates true.
    """

    #: The wrapped opval union object for this branch statement.
    wrapped: ComparisonOpvals = attrs.field()

    @classmethod
    @override
    def from_raw_command(cls, cmd: RawCommand) -> ConditionalBranchCommand:
        opcode_1 = cast(int, cmd.parameters[0])

        wrapped: ComparisonOpvals
        match opcode_1:
            case 0:  # Check Switch
                # e.g. 0, 7, 0 checks if switch 7 is on
                is_on = cmd.parameters[2] == 0
                wrapped = CheckSwitchOpval(switch_id=cast(int, cmd.parameters[1]), is_on=is_on)

            case 1:  # Check Variable
                # e.g. 1 18 0 2 0 checks if variable 18 is equal to 2
                # or 1 18 1 19 0 checks if variable 18 is equal to variable 19
                var_id = cast(int, cmd.parameters[1])
                opcode_2 = cast(int, cmd.parameters[2])
                opval = cast(int, cmd.parameters[3])
                opcode_3 = CompareVariableOpcode(cast(int, cmd.parameters[4]))

                if opcode_2 == 0:
                    wrapped = CompareVariableToConstantOpval(
                        variable_id=var_id, opcode=opcode_3, constant=opval
                    )
                elif opcode_2 == 1:
                    wrapped = CompareVariableToVariableOpval(
                        variable_id=var_id,
                        opcode=opcode_3,
                        other_variable_id=opval,
                    )
                else:
                    raise NotImplementedError(f"opcode_2 {opcode_2}")

            case 2:  # Check Self Switch
                var_name = cast(Literal["A", "B", "C", "D"], cmd.parameters[1])
                is_on = cmd.parameters[2] == 0
                wrapped = CheckSwitchOpval(switch_id=var_name, is_on=is_on)

            case 6:  # Check Facing
                actor = cast(int, cmd.parameters[1])
                direction = RgssDirection(cmd.parameters[2])
                wrapped = CheckFacingOpval(character_id=actor, direction=direction)

            case 12:  # Script
                wrapped = CheckScriptReturnOpval(script=cast(str, cmd.parameters[1]))

            case code:
                raise ValueError(f"unknown comparison opcode {code}")

        return ConditionalBranchCommand(indent=cmd.indent, wrapped=wrapped)

    @override
    def to_raw_command(self) -> RawCommand:
        params: list[RubyMarshalValue] = []

        if isinstance(self.wrapped, CheckSwitchOpval):
            if isinstance(self.wrapped.switch_id, str):
                params.append(2)  # Check Self Switch
                params.append(self.wrapped.switch_id)

            else:
                params.append(0)  # Check Switch
                params.append(self.wrapped.switch_id)

            params.append(0 if self.wrapped.is_on else 1)

        elif isinstance(self.wrapped, CheckFacingOpval):
            params = [6, self.wrapped.character_id, self.wrapped.direction.value]

        elif isinstance(self.wrapped, CheckScriptReturnOpval):
            params = [12, self.wrapped.script]

        else:
            # unify variable_id writing, the next code will overwrite params[2|3]
            params = [1, self.wrapped.variable_id, None, None, self.wrapped.opcode.value]

            if isinstance(self.wrapped, CompareVariableToConstantOpval):
                params[2] = 0  # Compare Variable To Constant
                params[3] = self.wrapped.constant
            else:
                params[2] = 1  # Compare Variable To Variable
                params[3] = self.wrapped.other_variable_id

        return RawCommand(code=111, parameters=params, indent=self.indent)

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {
            "command": "ConditionalBranchCommand",
            "type": type(self.wrapped).__name__,
            "comparison": converter.unstructure(self.wrapped),
        }


@attrs.define(kw_only=True)
@final
class EnterLoopCommand(RubyBaseEventCommand):
    """
    An event command that marks the start of a loop.
    """

    @classmethod
    @override
    def from_raw_command(cls, cmd: RawCommand) -> EnterLoopCommand:
        return EnterLoopCommand(indent=cmd.indent)

    @override
    def to_raw_command(self) -> RawCommand:
        return RawCommand(code=112, indent=self.indent)

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {"command": "EnterLoopCommand"}


@attrs.define(kw_only=True)
@final
class BreakLoopCommand(RubyBaseEventCommand):
    """
    An event command that breaks out of a loop.
    """

    @classmethod
    @override
    def from_raw_command(cls, cmd: RawCommand) -> BreakLoopCommand:
        return BreakLoopCommand(indent=cmd.indent)

    @override
    def to_raw_command(self) -> RawCommand:
        return RawCommand(code=113, indent=self.indent)

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {"command": "BreakLoopCommand"}


@attrs.define(kw_only=True)
class RepeatAboveCommand(RubyBaseEventCommand):
    """
    An event command that repeats the commands above it.
    """

    @classmethod
    @override
    def from_raw_command(cls, cmd: RawCommand) -> RepeatAboveCommand:
        return RepeatAboveCommand(indent=cmd.indent)

    @override
    def to_raw_command(self) -> RawCommand:
        return RawCommand(code=413, parameters=[], indent=self.indent)

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {"command": "RepeatAboveCommand"}


@attrs.define(kw_only=True)
class ExitEventProcesssingCommand(RubyBaseEventCommand):
    """
    An event command that stops processing the event.
    """

    @classmethod
    @override
    def from_raw_command(cls, cmd: RawCommand) -> ExitEventProcesssingCommand:
        return ExitEventProcesssingCommand(indent=cmd.indent)

    @override
    def to_raw_command(self) -> RawCommand:
        return RawCommand(code=115, indent=self.indent)

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {"command": "ExitEventProcesssingCommand"}


@attrs.define(kw_only=True)
@final
class EraseThisEventCommand(RubyBaseEventCommand):
    """
    An event command that (temporarily) erases the current event.
    """

    @classmethod
    @override
    def from_raw_command(cls, cmd: RawCommand) -> EraseThisEventCommand:
        return EraseThisEventCommand(indent=cmd.indent)

    @override
    def to_raw_command(self) -> RawCommand:
        return RawCommand(code=116, indent=self.indent)

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {"command": "EraseThisEventCommand"}


@attrs.define(kw_only=True)
@final
class CallCommonEventCommand(RubyBaseEventCommand):
    """
    An event command that calls a common event.
    """

    #: The ID of the common event to call.
    common_event_id: int = attrs.field()

    @classmethod
    @override
    def from_raw_command(cls, cmd: RawCommand) -> CallCommonEventCommand:
        return CallCommonEventCommand(
            common_event_id=cast(int, cmd.parameters[0]), indent=cmd.indent
        )

    @override
    def to_raw_command(self) -> RawCommand:
        return RawCommand(code=117, parameters=[self.common_event_id], indent=self.indent)

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {"command": "CallCommonEventCommand", "common_event_id": self.common_event_id}
