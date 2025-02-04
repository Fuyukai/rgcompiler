from __future__ import annotations

from typing import Any, cast, final, override

import attrs
from cattr import Converter

from rgss.rpg.commands.base import RawCommand, RubyBaseEventCommand
from rgss.types import RgssDirection
from rhodochrosite.ruby import RubyMarshalValue, RubySymbol


@attrs.define(kw_only=True)
class DirectTransferPlayerCommand(RubyBaseEventCommand):
    """
    An event command that transfers the player to a different map.

    This is the variant that doesn't use variables.
    """

    map_id: int = attrs.field()
    x: int = attrs.field()
    y: int = attrs.field()
    direction: RgssDirection = attrs.field(converter=RgssDirection)
    no_fade: bool = attrs.field()

    @classmethod
    @override
    def from_raw_command(cls, cmd: RawCommand) -> DirectTransferPlayerCommand:
        return DirectTransferPlayerCommand(
            map_id=cast(int, cmd.parameters[1]),
            x=cast(int, cmd.parameters[2]),
            y=cast(int, cmd.parameters[3]),
            direction=RgssDirection(cast(int, cmd.parameters[4])),
            no_fade=cmd.parameters[5] == 1,
            indent=cmd.indent,
        )

    @override
    def to_raw_command(self) -> RawCommand:
        return RawCommand(
            code=201,
            parameters=[0, self.map_id, self.x, self.y, self.direction.value, int(self.no_fade)],
            indent=self.indent,
        )

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {
            "command": "TransferPlayerCommand",
            "map_id": self.map_id,
            "x": self.x,
            "y": self.y,
            "direction": self.direction.name,
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
    direction: RgssDirection = attrs.field(converter=RgssDirection)
    no_fade: bool = attrs.field()

    @classmethod
    @override
    def from_raw_command(cls, cmd: RawCommand) -> VariableTransferPlayerCommand:
        return VariableTransferPlayerCommand(
            map_id_variable=cast(int, cmd.parameters[1]),
            x_variable=cast(int, cmd.parameters[2]),
            y_variable=cast(int, cmd.parameters[3]),
            direction=cast(int, cmd.parameters[4]),
            no_fade=cmd.parameters[5] == 1,
            indent=cmd.indent,
        )

    @override
    def to_raw_command(self) -> RawCommand:
        return RawCommand(
            code=201,
            parameters=[
                1,
                self.map_id_variable,
                self.x_variable,
                self.y_variable,
                self.direction.value,
                int(self.no_fade),
            ],
            indent=self.indent,
        )

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {
            "command": "VariableTransferPlayerCommand",
            "map_id_variable": self.map_id_variable,
            "x_variable": self.x_variable,
            "y_variable": self.y_variable,
            "direction": self.direction.name,
            "no_fade": self.no_fade,
        }


def make_transfer_command(_: RubySymbol, raw: RawCommand) -> RubyBaseEventCommand:
    assert raw.parameters[0] in (0, 1), (
        f"expected first param of code 201 to be (0, 1), not {raw.parameters[0]}"
    )
    uses_variables = raw.parameters[0] == 1

    if uses_variables:
        return VariableTransferPlayerCommand.from_raw_command(raw)

    return DirectTransferPlayerCommand.from_raw_command(raw)


@attrs.define(kw_only=True)
class SetEventLocationAbsolute:
    """
    Sets the absolute location of an event.
    """

    x: int = attrs.field()
    y: int = attrs.field()


@attrs.define(kw_only=True)
class SetEventLocationVariables:
    """
    Sets the location of an event using other variables.
    """

    x_var_id: int = attrs.field()
    y_var_id: int = attrs.field()


@attrs.define(kw_only=True)
class SetEventLocationSwap:
    """
    Sets the location of an event by swapping it with another event.
    """

    event_id: int = attrs.field()


@attrs.define(kw_only=True)
@final
class SetEventLocationCommand(RubyBaseEventCommand):
    """
    An event command that sets the temporary location of an event.
    """

    #: The ID of the event to move.
    #:
    #: ``0`` refers to this event; ``-1`` refers to the player.
    event_id: int = attrs.field()

    #: The actual value to move the event to using.
    opval: SetEventLocationAbsolute | SetEventLocationVariables | SetEventLocationSwap = (
        attrs.field()
    )

    #: The resulting direction for the transferred event.
    direction: RgssDirection = attrs.field()

    @classmethod
    @override
    def from_raw_command(cls, cmd: RawCommand) -> SetEventLocationCommand:
        event_id = cast(int, cmd.parameters[0])
        opcode = cast(int, cmd.parameters[1])
        direction = RgssDirection(cmd.parameters[4])

        match opcode:
            case 0:
                opval = SetEventLocationAbsolute(
                    x=cast(int, cmd.parameters[2]), y=cast(int, cmd.parameters[3])
                )

            case 1:
                opval = SetEventLocationVariables(
                    x_var_id=cast(int, cmd.parameters[2]), y_var_id=cast(int, cmd.parameters[3])
                )

            case 2:
                # unusually generous for RGXP to keep this as 5 items long.
                opval = SetEventLocationSwap(event_id=cast(int, cmd.parameters[2]))

            case code:
                raise ValueError(f"can't do {code} for set event location!")

        return SetEventLocationCommand(
            event_id=event_id, opval=opval, direction=direction, indent=cmd.indent
        )

    @override
    def to_raw_command(self) -> RawCommand:
        params: list[RubyMarshalValue] = [self.event_id]

        if isinstance(self.opval, SetEventLocationAbsolute):
            params.extend([0, self.opval.x, self.opval.y])
        elif isinstance(self.opval, SetEventLocationVariables):
            params.extend([1, self.opval.x_var_id, self.opval.y_var_id])
        else:
            params.extend([2, self.opval.event_id, 0])

        params.append(self.direction.value)
        return RawCommand(code=202, parameters=params, indent=self.indent)

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {
            "command": "SetEventLocationCommand",
            "event_id": self.event_id,
            "opval": converter.unstructure(self.opval),
            "direction": self.direction.name,
        }
