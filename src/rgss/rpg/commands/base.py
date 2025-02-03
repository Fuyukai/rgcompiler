import abc
from typing import Any, Self, final, override

import attrs
from cattr import Converter

from rhodochrosite.ruby import RubyMarshalValue, RubySymbol, RubyUserObject, atom

RPG_EVENT_COMMAND = atom("RPG::EventCommand")
RPG_MOVE_COMMAND = atom("RPG::MoveCommand")

PARAMS_SYMBOL = atom("@parameters")
INDENT_SYMBOL = atom("@indent")
CODE_SYMBOL = atom("@code")


@attrs.define(kw_only=True, frozen=True, eq=True)
@final
class RawCommand:
    """
    The raw underlying value for both a ``RPG::EventCommand`` and a ``RPG::MoveCommand``.
    """

    #: The code for this command.
    #:
    #: Three-digit codes are event commands, and two-digit codes are move commands.
    code: int = attrs.field()

    #: The arbitrary block of Ruby value parameters for this command.
    parameters: list[RubyMarshalValue] = attrs.field(factory=list)

    #: The "indent" for this command. Ignored, and is only used in the editor for event commands.
    indent: int = attrs.field()


class RubyBaseCommand(RubyUserObject, abc.ABC):
    """
    A command object that can be made from and turned into a :class:`.RawCommand`.
    """

    @classmethod
    @abc.abstractmethod
    def from_raw_command(cls, cmd: RawCommand) -> Self:
        """
        Creates a new command object from a :class:`.RawCommand`.
        """

    @abc.abstractmethod
    def to_raw_command(self) -> RawCommand:
        """
        Gets the actual :class:`.RawCommand` that will be marshalled.
        """

    @abc.abstractmethod
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        """
        Converts this object to a dictionary.
        """

        return {
            "command": type(self).__name__,
            "raw": converter.unstructure(self.to_raw_command()),
        }

    @override
    def find_instance_variables(self) -> list[tuple[RubySymbol, RubyMarshalValue]]:
        cmd = self.to_raw_command()
        return [
            (PARAMS_SYMBOL, cmd.parameters),
            (INDENT_SYMBOL, cmd.indent),
            (CODE_SYMBOL, cmd.code),
        ]


@attrs.define(kw_only=True)
class RubyBaseEventCommand(RubyBaseCommand, abc.ABC):
    """
    A single event command in an event.
    """

    indent: int = attrs.field()

    @property
    @override
    def ruby_class_name(self) -> RubySymbol:
        return RPG_EVENT_COMMAND


class RubyBaseMoveCommand(RubyBaseCommand, abc.ABC):
    """
    A single move command wrapped inside an event or event command.
    """

    @property
    @override
    def ruby_class_name(self) -> RubySymbol:
        return RPG_EVENT_COMMAND

    @override
    def find_instance_variables(self) -> list[tuple[RubySymbol, RubyMarshalValue]]:
        cmd = self.to_raw_command()
        return [
            (PARAMS_SYMBOL, cmd.parameters),
            (CODE_SYMBOL, cmd.code),
        ]
