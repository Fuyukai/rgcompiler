from __future__ import annotations

import abc
from typing import Any, Self, cast, final, override

import attr
import attrs
from cattr import Converter

from rhodochrosite.ruby import RubyMarshalValue, RubySymbol, RubyUserObject, atom

RPG_EVENT_COMMAND = atom("RPG::EventCommand")

PARAMS_SYMBOL = atom("@parameters")
INDENT_SYMBOL = atom("@indent")
CODE_SYMBOL = atom("@code")

# Design note: This is extremely awkward...


@attr.define(frozen=True, eq=True)
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


@final
class EmptyEventCommand(RubyBaseEventCommand):
    """
    An event command that is empty.

    This is used for events with no events.
    """

    @classmethod
    @override
    def from_raw_event_command(cls, cmd: RawEventCommand) -> EmptyEventCommand:
        return EmptyEventCommand()

    @override
    def get_raw_event_command(self) -> RawEventCommand:
        return RawEventCommand(code=0)

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {"command": "EmptyEventCommand"}


@attr.define(kw_only=True)
@final
class UnknownEventCommand(RubyBaseEventCommand):
    """
    An event command that is currently unknown.
    """

    raw: RawEventCommand = attr.field()

    @classmethod
    @override
    def from_raw_event_command(cls, cmd: RawEventCommand) -> UnknownEventCommand:
        return UnknownEventCommand(raw=cmd)

    @override
    def get_raw_event_command(self) -> RawEventCommand:
        return self.raw

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return super().unstructure(converter)


@attr.define(kw_only=True)
class ShowDialogueCommand(RubyBaseEventCommand):
    """
    An event command that shows dialogue to the player.
    """

    text: str = attr.field()

    @classmethod
    @override
    def from_raw_event_command(cls, cmd: RawEventCommand) -> ShowDialogueCommand:
        return ShowDialogueCommand(text=cast(str, cmd.parameters[0]))

    @override
    def get_raw_event_command(self) -> RawEventCommand:
        return RawEventCommand(
            code=101,
            parameters=[self.text],
        )

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {
            "command": "ShowDialogueCommand",
            "text": self.text,
        }


@attr.define(kw_only=True)
class ContinueDialogueCommand(ShowDialogueCommand):
    """
    An event command that continues dialogue.
    """

    @classmethod
    @override
    def from_raw_event_command(cls, cmd: RawEventCommand) -> ContinueDialogueCommand:
        return ContinueDialogueCommand(text=cast(str, cmd.parameters[0]))

    @override
    def get_raw_event_command(self) -> RawEventCommand:
        return RawEventCommand(
            code=401,
            parameters=[self.text],
        )

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {
            "command": "ContinueDialogueCommand",
            "text": self.text,
        }


COMMAND_MAPPING: dict[int, type[RubyBaseEventCommand]] = {
    0: EmptyEventCommand,
    101: ShowDialogueCommand,
    401: ContinueDialogueCommand,
}


def make_event_command_from_ivars(
    _: RubySymbol, ivars: dict[RubySymbol, RubyMarshalValue]
) -> RubyBaseEventCommand:
    code = cast(int, ivars[CODE_SYMBOL])
    return COMMAND_MAPPING.get(code, UnknownEventCommand).from_raw_event_command(
        RawEventCommand(
            code=code,
            parameters=cast(list[RubyMarshalValue], ivars[PARAMS_SYMBOL]),
            indent=cast(int, ivars[INDENT_SYMBOL]),
        )
    )
