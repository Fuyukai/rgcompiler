from __future__ import annotations

from typing import Any, Literal, cast, override

import attrs
from cattr import Converter

from rgss.rpg.commands.base import RawEventCommand, RubyBaseEventCommand


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
    def from_raw_event_command(cls, cmd: RawEventCommand) -> SetSwitchCommand:
        return SetSwitchCommand(
            switch_start=cast(int, cmd.parameters[0]),
            switch_end=cast(int, cmd.parameters[1]),
            # THIS IS CORRECT, FOR SOME STUPID FUCKING REASON IT'S INVERTED?
            switch_value=cmd.parameters[2] == 0,
        )

    @override
    def get_raw_event_command(self) -> RawEventCommand:
        return RawEventCommand(
            code=121,
            parameters=[self.switch_start, self.switch_end, int(not self.switch_value)],
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
    def from_raw_event_command(cls, cmd: RawEventCommand) -> SetSelfSwitchCommand:
        return SetSelfSwitchCommand(
            switch=cast(Literal["A", "B", "C", "D"], cmd.parameters[0]),
            switch_value=cmd.parameters[1] == 0,
        )

    @override
    def get_raw_event_command(self) -> RawEventCommand:
        return RawEventCommand(
            code=123,
            parameters=[self.switch, int(not self.switch_value)],
        )

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {
            "command": "SetSelfSwitchCommand",
            "switch": self.switch,
            "switch_value": self.switch_value,
        }
