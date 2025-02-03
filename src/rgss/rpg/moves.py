from typing import final, override

import attrs

from rgss.rpg.commands.base import RubyBaseMoveCommand
from rhodochrosite.ruby import RubySymbol, RubyUserObject, atom, ruby_name

RPG_MOVE_ROUTE = atom("RPG::MoveRoute")


@attrs.define(kw_only=True)
@final
class RubyMoveRoute(RubyUserObject):
    """
    A move route for an event.

    This is also re-used for the Move Route event command.
    """

    skippable: bool = attrs.field(default=False)
    repeat: bool = attrs.field(default=False)

    moves: list[RubyBaseMoveCommand] = attrs.field(factory=list, metadata=ruby_name("list"))

    @property
    @override
    def ruby_class_name(self) -> RubySymbol:
        return RPG_MOVE_ROUTE
