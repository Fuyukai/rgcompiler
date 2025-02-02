import abc
from typing import Any, Self, final, override

import attrs
from cattr import Converter

from rhodochrosite.ruby import RubyMarshalValue, RubySymbol, RubyUserObject, atom

RPG_EVENT_COMMAND = atom("RPG::EventCommand")

PARAMS_SYMBOL = atom("@parameters")
INDENT_SYMBOL = atom("@indent")
CODE_SYMBOL = atom("@code")


@attrs.define(frozen=True, eq=True)
@final
class RawEventCommand:
    """
    The raw underlying value for a ``RPG::EventCommand``.
    """

    code: int = attrs.field()
    parameters: list[RubyMarshalValue] = attrs.field(factory=list)
    indent: int = attrs.field(default=0)


class RubyBaseEventCommand(RubyUserObject, abc.ABC):
    """
    A single event command in an event.
    """

    @classmethod
    @abc.abstractmethod
    def from_raw_event_command(cls, cmd: RawEventCommand) -> Self:
        """
        Creates a new :class:`.RubyBaseEventCommand` from a :class:`.RawEventCommand`.
        """

    @abc.abstractmethod
    def get_raw_event_command(self) -> RawEventCommand:
        """
        Gets the actual :class:`.RawEventCommand` that will be serialised.
        """

    @abc.abstractmethod
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        """
        Converts this object to a dictionary.
        """

        return {
            "command": type(self).__name__,
            "raw": converter.unstructure(self.get_raw_event_command()),
        }

    @property
    @override
    def ruby_class_name(self) -> RubySymbol:
        return RPG_EVENT_COMMAND

    @override
    def find_instance_variables(self) -> list[tuple[RubySymbol, RubyMarshalValue]]:
        cmd = self.get_raw_event_command()
        return [
            (PARAMS_SYMBOL, cmd.parameters),
            (INDENT_SYMBOL, cmd.indent),
            (CODE_SYMBOL, cmd.code),
        ]
