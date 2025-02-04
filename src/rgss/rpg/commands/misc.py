from __future__ import annotations

from typing import Any, cast, final, override

import attrs
from cattr import Converter

from rgss.rpg.commands.base import (
    RPG_EVENT_COMMAND,
    RawCommand,
    RubyBaseCommand,
    RubyBaseEventCommand,
)
from rgss.rpg.moves import RubyMoveRoute
from rhodochrosite.ruby import RubyMarshalValue, RubySymbol


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
    def from_raw_command_and_type(cls, type: RubySymbol, cmd: RawCommand) -> EmptyCommand:
        return cls(symbol=type, raw=cmd)

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
    def from_raw_command_and_type(cls, type: RubySymbol, cmd: RawCommand) -> UnknownCommand:
        return cls(name=type, raw=cmd)

    @override
    def to_raw_command(self) -> RawCommand:
        return self.raw

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return super().unstructure(converter)


@attrs.define(kw_only=True)
class WaitCommand(RubyBaseCommand):
    """
    An event or move command that waits for a certain number of frames.
    """

    type: RubySymbol = attrs.field()
    frames: int = attrs.field()
    indent: int = attrs.field()

    @classmethod
    @override
    def from_raw_command_and_type(cls, type: RubySymbol, cmd: RawCommand) -> WaitCommand:
        return WaitCommand(type=type, frames=cast(int, cmd.parameters[0]), indent=cmd.indent)

    @property
    @override
    def ruby_class_name(self) -> RubySymbol:
        return self.type

    @override
    def to_raw_command(self) -> RawCommand:
        code = 106 if self.type == RPG_EVENT_COMMAND else 15
        return RawCommand(code=code, parameters=[self.frames], indent=self.indent)

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

    #: The ID of the event to set the route of.
    #:
    #: If this is the special constant "0", it refers to the current event. If this is the special
    #: constant "-1", it refers to the current player.
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


@attrs.define(kw_only=True)
@final
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


@attrs.define(kw_only=True)
@final
class RecoverAllCommand(RubyBaseEventCommand):
    """
    An event command that recovers all of the stats for a specific actor.

    For Reborn, this is the same as visiting a Pokémon Center.
    """

    #: The ID of the actor to recover.
    #:
    #: If this is the special constant "0", it refers to the whole party.
    actor_id: int = attrs.field()

    @classmethod
    @override
    def from_raw_command(cls, cmd: RawCommand) -> RecoverAllCommand:
        return RecoverAllCommand(actor_id=cast(int, cmd.parameters[0]), indent=cmd.indent)

    @override
    def to_raw_command(self) -> RawCommand:
        return RawCommand(code=314, parameters=[self.actor_id], indent=self.indent)

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {"command": "RecoverAllCommand", "actor_id": self.actor_id}


@attrs.define(kw_only=True, frozen=True)
class PanoramaSetting:
    name: str = attrs.field()
    hue: int = attrs.field()


@attrs.define(kw_only=True, frozen=True)
class FogSetting:
    name: str = attrs.field()
    hue: int = attrs.field()
    opacity: int = attrs.field()
    blend_type: int = attrs.field()
    zoom: int = attrs.field()
    sx: int = attrs.field()
    sy: int = attrs.field()


@attrs.define(kw_only=True, frozen=True)
class BattlebackSetting:
    name: str = attrs.field()


@attrs.define(kw_only=True)
@final
class ChangeMapSettingsCommand(RubyBaseEventCommand):
    """
    An event command that changes settings for how the map is rendered.
    """

    #: The actual setting being set.
    setting: PanoramaSetting | FogSetting | BattlebackSetting = attrs.field()

    @classmethod
    @override
    def from_raw_command(cls, cmd: RawCommand) -> ChangeMapSettingsCommand:
        opcode = cast(int, cmd.parameters[0])
        name = cast(str, cmd.parameters[1])

        match opcode:
            case 0:
                opval = PanoramaSetting(name=name, hue=cast(int, cmd.parameters[2]))

            case 1:
                opval = FogSetting(
                    name=name,
                    hue=cast(int, cmd.parameters[2]),
                    opacity=cast(int, cmd.parameters[3]),
                    blend_type=cast(int, cmd.parameters[4]),
                    zoom=cast(int, cmd.parameters[5]),
                    sx=cast(int, cmd.parameters[6]),
                    sy=cast(int, cmd.parameters[7]),
                )

            case 2:
                opval = BattlebackSetting(name=name)

            case code:
                raise ValueError(f"can't handle opcode {code} for changing map settings!")

        return ChangeMapSettingsCommand(
            setting=opval,
            indent=cmd.indent,
        )

    @override
    def to_raw_command(self) -> RawCommand:
        parameters: list[RubyMarshalValue] = [None, self.setting.name]

        if isinstance(self.setting, PanoramaSetting):
            parameters[0] = 0
            parameters.append(self.setting.hue)
        elif isinstance(self.setting, FogSetting):
            parameters[0] = 1
            parameters.extend([
                self.setting.hue,
                self.setting.opacity,
                self.setting.blend_type,
                self.setting.zoom,
                self.setting.sx,
                self.setting.sy,
            ])
        else:
            parameters[0] = 2

        return RawCommand(
            code=204,
            parameters=parameters,
            indent=self.indent,
        )

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {
            "command": "ChangeMapSettingsCommand",
            "setting": converter.unstructure(self.setting),
        }
