from __future__ import annotations

from typing import Any, cast, final, override

import attrs
from cattr import Converter

from rgss.rpg.commands.base import RawCommand, RubyBaseCommand, RubyBaseEventCommand
from rgss.rpg.moves import RubyMoveRoute
from rhodochrosite.ruby import RubySymbol


@attrs.define(kw_only=True)
@final
class EmptyCommand(RubyBaseCommand):
    """
    An event command that is empty.

    This is used for events with no events.
    """

    symbol: RubySymbol = attrs.field()
    raw: RawCommand = attrs.field()

    @property
    @override
    def ruby_class_name(self) -> RubySymbol:
        return self.symbol

    @classmethod
    @override
    def from_raw_command(cls, cmd: RawCommand) -> EmptyCommand:
        raise NotImplementedError("Can't do this with the empty command")

    @override
    def to_raw_command(self) -> RawCommand:
        return RawCommand(code=0, indent=self.raw.indent)

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {"command": "EmptyCommand"}


@attrs.define(kw_only=True)
@final
class UnknownCommand(RubyBaseCommand):
    """
    An event command that is currently unknown.
    """

    name: RubySymbol = attrs.field()
    raw: RawCommand = attrs.field()

    @property
    @override
    def ruby_class_name(self) -> RubySymbol:
        return self.name

    @classmethod
    @override
    def from_raw_command(cls, cmd: RawCommand) -> UnknownCommand:
        raise NotImplementedError("Special form can't be made using from_raw_command")

    @override
    def to_raw_command(self) -> RawCommand:
        return self.raw

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return super().unstructure(converter)


@attrs.define(kw_only=True)
class WaitCommand(RubyBaseEventCommand):
    """
    An event command that waits for a certain number of frames.
    """

    frames: int = attrs.field()

    @classmethod
    @override
    def from_raw_command(cls, cmd: RawCommand) -> WaitCommand:
        return WaitCommand(frames=cast(int, cmd.parameters[0]), indent=cmd.indent)

    @override
    def to_raw_command(self) -> RawCommand:
        return RawCommand(code=106, parameters=[self.frames], indent=self.indent)

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {
            "command": "WaitCommand",
            "frames": self.frames,
        }


@attrs.define(kw_only=True)
class InlineRubyCommand(RubyBaseEventCommand):
    """
    An event command that runs a Ruby script.
    """

    script: str = attrs.field()

    @classmethod
    @override
    def from_raw_command(cls, cmd: RawCommand) -> InlineRubyCommand:
        return InlineRubyCommand(script=cast(str, cmd.parameters[0]), indent=cmd.indent)

    @override
    def to_raw_command(self) -> RawCommand:
        return RawCommand(code=355, parameters=[self.script], indent=self.indent)

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {
            "command": "InlineRubyCommand",
            "script": self.script,
        }


@attrs.define(kw_only=True)
class InlineRubyContinuedCommand(RubyBaseEventCommand):
    """
    Like :class:`.InlineRubyCommand`, but continued onto the next editor line.
    """

    script: str = attrs.field()

    @classmethod
    @override
    def from_raw_command(cls, cmd: RawCommand) -> InlineRubyContinuedCommand:
        return InlineRubyContinuedCommand(script=cast(str, cmd.parameters[0]), indent=cmd.indent)

    @override
    def to_raw_command(self) -> RawCommand:
        return RawCommand(code=655, parameters=[self.script], indent=self.indent)

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {
            "command": "InlineRubyContinuedCommand",
            "script": self.script,
        }


@attrs.define(kw_only=True)
class SetMoveRouteCommand(RubyBaseEventCommand):
    """
    An event command that sets the move route of another event.
    """

    event_id: int = attrs.field()
    move_route: RubyMoveRoute = attrs.field()

    @classmethod
    @override
    def from_raw_command(cls, cmd: RawCommand) -> SetMoveRouteCommand:
        return SetMoveRouteCommand(
            event_id=cast(int, cmd.parameters[0]),
            move_route=cast(RubyMoveRoute, cmd.parameters[1]),
            indent=cmd.indent,
        )

    @override
    def to_raw_command(self) -> RawCommand:
        return RawCommand(code=209, parameters=[self.event_id, self.move_route], indent=self.indent)

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {
            "command": "SetMoveRouteCommand",
            "event_id": self.event_id,
            "move_route": converter.unstructure(self.move_route),
        }


@attrs.define(kw_only=True)
class VisualMoveRouteCommand(RubyBaseEventCommand):
    """
    An event command that contains a single move route. This command is not bound to an event.

    The differernce between this class and the other move route class is unknown, but the official
    editor seems to emit both? This command is likely entirely visual for editor purposes.
    """

    move_route: RubyMoveRoute = attrs.field()

    @classmethod
    @override
    def from_raw_command(cls, cmd: RawCommand) -> VisualMoveRouteCommand:
        return VisualMoveRouteCommand(
            move_route=cast(RubyMoveRoute, cmd.parameters[0]), indent=cmd.indent
        )

    @override
    def to_raw_command(self) -> RawCommand:
        return RawCommand(code=509, parameters=[self.move_route], indent=self.indent)

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {
            "command": "VisualMoveRouteCommand",
            "move_route": converter.unstructure(self.move_route),
        }


class WaitForMoveCompletionCommand(RubyBaseEventCommand):
    """
    Waits for the move route to complete.
    """

    @classmethod
    @override
    def from_raw_command(cls, cmd: RawCommand) -> WaitForMoveCompletionCommand:
        return WaitForMoveCompletionCommand(indent=cmd.indent)

    @override
    def to_raw_command(self) -> RawCommand:
        return RawCommand(code=210, parameters=[], indent=self.indent)

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {"command": "WaitForMoveCompletionCommand"}
