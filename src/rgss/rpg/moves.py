from typing import final, override

import attrs

from rhodochrosite.ruby import GenericRubyUserObject, RubySymbol, RubyUserObject, atom, ruby_name

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

    moves: list[GenericRubyUserObject] = attrs.field(factory=list, metadata=ruby_name("list"))

    @property
    @override
    def ruby_class_name(self) -> RubySymbol:
        return RPG_MOVE_ROUTE

