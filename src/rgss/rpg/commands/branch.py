from __future__ import annotations

from typing import Any, override

import attrs
from cattrs import Converter

from rgss.rpg.commands.base import RawCommand, RubyBaseEventCommand

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
# This is *not* the case for RPG Maker branches. They are implemented with a set of extra
# instructions directly in a list like so:
#
# ConditionalBranch
#   Op1
#   Op2
#   ...
# Else
#   Op3
#   Op4
# ConditionalEnd
#
# There is *no* branching involved; if the conditional fails then the interpreter will just skip
# ahead until it finds an Else instruction and then start executing. If the conditional didn't
# fail, it will seek from the Else instruction to the matching ConditionalEnd instruction.


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
