from __future__ import annotations

from typing import Any, cast, final, override

import attrs
from cattr import Converter

from rgss.rpg.commands.base import RawCommand, RubyBaseEventCommand
from rgss.types import RgssDirection
from rhodochrosite.ruby import RubyMarshalValue


@attrs.define(kw_only=True, frozen=True)
class TransferDirect:
    x: int = attrs.field()
    y: int = attrs.field()


@attrs.define(kw_only=True, frozen=True)
class TransferByVariable:
    x_variable: int = attrs.field()
    y_variable: int = attrs.field()


@attrs.define(kw_only=True)
@final
class TransferPlayerCommand(RubyBaseEventCommand):
    """
    An event command that transfers the player to a different position, possibly on another map.
    """

    map_id: int = attrs.field()
    opval: TransferDirect | TransferByVariable = attrs.field()
    direction: RgssDirection = attrs.field(converter=RgssDirection)
    no_fade: bool = attrs.field()

    @classmethod
    @override
    def from_raw_command(cls, cmd: RawCommand) -> TransferPlayerCommand:
        map_id = cast(int, cmd.parameters[1])
        direction = RgssDirection(cmd.parameters[4])
        no_fade = cmd.parameters[5] == 1

        x = cast(int, cmd.parameters[2])
        y = cast(int, cmd.parameters[3])

        uses_variables = cmd.parameters[0] == 1
        if uses_variables:
            opval = TransferByVariable(x_variable=x, y_variable=y)
        else:
            opval = TransferDirect(x=x, y=y)

        return TransferPlayerCommand(
            map_id=map_id, opval=opval, direction=direction, no_fade=no_fade, indent=cmd.indent
        )

    @override
    def to_raw_command(self) -> RawCommand:
        params: list[RubyMarshalValue] = [0, self.map_id]

        if isinstance(self.opval, TransferDirect):
            params.extend([self.opval.x, self.opval.y])
        else:
            params.extend([self.opval.x_variable, self.opval.y_variable])

        params.extend([self.direction.value, int(self.no_fade)])
        return RawCommand(code=201, parameters=params, indent=self.indent)

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {
            "command": "TransferPlayerCommand",
            "map_id": self.map_id,
            "opval": converter.unstructure(self.opval),
            "direction": self.direction.name,
            "no_fade": self.no_fade,
        }


@attrs.define(kw_only=True)
class TransferSwap:
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
    opval: TransferDirect | TransferByVariable | TransferSwap = attrs.field()

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
                opval = TransferDirect(
                    x=cast(int, cmd.parameters[2]), y=cast(int, cmd.parameters[3])
                )

            case 1:
                opval = TransferByVariable(
                    x_variable=cast(int, cmd.parameters[2]), y_variable=cast(int, cmd.parameters[3])
                )

            case 2:
                # unusually generous for RGXP to keep this as 5 items long.
                opval = TransferSwap(event_id=cast(int, cmd.parameters[2]))

            case code:
                raise ValueError(f"can't do {code} for set event location!")

        return SetEventLocationCommand(
            event_id=event_id, opval=opval, direction=direction, indent=cmd.indent
        )

    @override
    def to_raw_command(self) -> RawCommand:
        params: list[RubyMarshalValue] = [self.event_id]

        if isinstance(self.opval, TransferDirect):
            params.extend([0, self.opval.x, self.opval.y])
        elif isinstance(self.opval, TransferByVariable):
            params.extend([1, self.opval.x_variable, self.opval.y_variable])
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
