from __future__ import annotations

from typing import Any, cast, override

import attrs
from cattr import Converter

from rgss.rpg.commands.base import RawEventCommand, RubyBaseEventCommand


@attrs.define(kw_only=True)
class DirectTransferPlayerCommand(RubyBaseEventCommand):
    """
    An event command that transfers the player to a different map.

    This is the variant that doesn't use variables.
    """

    map_id: int = attrs.field()
    x: int = attrs.field()
    y: int = attrs.field()
    direction: int = attrs.field()
    no_fade: bool = attrs.field()

    @classmethod
    @override
    def from_raw_event_command(cls, cmd: RawEventCommand) -> DirectTransferPlayerCommand:
        return DirectTransferPlayerCommand(
            map_id=cast(int, cmd.parameters[1]),
            x=cast(int, cmd.parameters[2]),
            y=cast(int, cmd.parameters[3]),
            direction=cast(int, cmd.parameters[4]),
            no_fade=cmd.parameters[5] == 1,
        )

    @override
    def get_raw_event_command(self) -> RawEventCommand:
        return RawEventCommand(
            code=201,
            parameters=[0, self.map_id, self.x, self.y, self.direction, int(self.no_fade)],
        )

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {
            "command": "TransferPlayerCommand",
            "map_id": self.map_id,
            "x": self.x,
            "y": self.y,
            "direction": self.direction,
            "no_fade": self.no_fade,
        }


@attrs.define(kw_only=True)
class VariableTransferPlayerCommand(RubyBaseEventCommand):
    """
    An event command that transfers the player to a different map.

    This is the variant that uses variables instead of a direct map ID.
    """

    map_id_variable: int = attrs.field()
    x_variable: int = attrs.field()
    y_variable: int = attrs.field()
    direction: int = attrs.field()
    no_fade: bool = attrs.field()

    @classmethod
    @override
    def from_raw_event_command(cls, cmd: RawEventCommand) -> VariableTransferPlayerCommand:
        return VariableTransferPlayerCommand(
            map_id_variable=cast(int, cmd.parameters[1]),
            x_variable=cast(int, cmd.parameters[2]),
            y_variable=cast(int, cmd.parameters[3]),
            direction=cast(int, cmd.parameters[4]),
            no_fade=cmd.parameters[5] == 1,
        )

    @override
    def get_raw_event_command(self) -> RawEventCommand:
        return RawEventCommand(
            code=201,
            parameters=[
                1,
                self.map_id_variable,
                self.x_variable,
                self.y_variable,
                self.direction,
                int(self.no_fade),
            ],
        )

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {
            "command": "VariableTransferPlayerCommand",
            "map_id_variable": self.map_id_variable,
            "x_variable": self.x_variable,
            "y_variable": self.y_variable,
            "direction": self.direction,
            "no_fade": self.no_fade,
        }


def make_transfer_command(raw: RawEventCommand) -> RubyBaseEventCommand:
    assert raw.parameters[0] in (0, 1), (
        f"expected first param of code 201 to be (0, 1), not {raw.parameters[0]}"
    )
    uses_variables = raw.parameters[0] == 1

    if uses_variables:
        return VariableTransferPlayerCommand.from_raw_event_command(raw)

    return DirectTransferPlayerCommand.from_raw_event_command(raw)
