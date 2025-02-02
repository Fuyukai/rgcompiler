from __future__ import annotations

from typing import Any, cast, final, override

import attrs
from cattr import Converter

from rgss.rpg.commands.base import RawEventCommand, RubyBaseEventCommand


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


@attrs.define(kw_only=True)
@final
class UnknownEventCommand(RubyBaseEventCommand):
    """
    An event command that is currently unknown.
    """

    raw: RawEventCommand = attrs.field()

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


@attrs.define(kw_only=True)
class WaitCommand(RubyBaseEventCommand):
    """
    An event command that waits for a certain number of frames.
    """

    frames: int = attrs.field()

    @classmethod
    @override
    def from_raw_event_command(cls, cmd: RawEventCommand) -> WaitCommand:
        return WaitCommand(frames=cast(int, cmd.parameters[0]))

    @override
    def get_raw_event_command(self) -> RawEventCommand:
        return RawEventCommand(code=106, parameters=[self.frames])

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
    def from_raw_event_command(cls, cmd: RawEventCommand) -> InlineRubyCommand:
        return InlineRubyCommand(script=cast(str, cmd.parameters[0]))

    @override
    def get_raw_event_command(self) -> RawEventCommand:
        return RawEventCommand(code=355, parameters=[self.script])

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {
            "command": "InlineRubyCommand",
            "script": self.script,
        }
