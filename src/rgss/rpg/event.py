from typing import Literal, final, override

import attrs

from rgss.rpg.commands.base import RubyBaseEventCommand
from rhodochrosite.ruby import GenericRubyUserObject, RubySymbol, RubyUserObject, atom, ruby_name

RPG_EVENT = atom("RPG::Event")
RPG_EVENT_PAGE = atom("RPG::Event::Page")
RPG_EVENT_CONDITION = atom("RPG::Event::Page::Condition")
RPG_EVENT_GRAPHIC = atom("RPG::Event::Page::Graphic")


@attrs.define()
@final
class RubyEventPageCondition(RubyUserObject):
    """
    The condition for an event page.
    """

    switch1_valid: bool = attrs.field(default=False)
    switch2_valid: bool = attrs.field(default=False)
    variable_valid: bool = attrs.field(default=False)
    self_switch_valid: bool = attrs.field(default=False)

    switch1_id: int = attrs.field(default=1)
    switch2_id: int = attrs.field(default=1)
    variable_id: int = attrs.field(default=1)
    variable_value: int = attrs.field(default=0)

    self_switch_ch: Literal["A", "B", "C", "D"] = attrs.field(default="A")

    @property
    @override
    def ruby_class_name(self) -> RubySymbol:
        return RPG_EVENT_CONDITION


@attrs.define()
@final
class RubyEventGraphic(RubyUserObject):
    """
    A graphic for an event. This is per-page.
    """

    #: The "character name" for this graphic.
    #:
    #: References a file in ``Graphics/Character``.
    character_name: str = attrs.field(default="")

    #: The tile ID in the current map's tileset for this event, if any.
    tile_id: int = attrs.field(default=0)

    #: The adjusted hue (of HSL) of the graphic.
    character_hue: int = attrs.field(default=0)

    #: The direction of the graphic.
    #:
    #: This is a number between 1 and 8, representing one of the cardinal directions; this will
    #: index into the rows of the graphic file. If the graphic file only has four rows, this number
    #: is divided by two to get the appropriate sprite.
    direction: int = attrs.field(default=2)

    #: The "pattern" of the graphic.
    #:
    #: This is a zero-indexed value that will index into the columns of the graphic file.
    pattern: int = attrs.field(default=0)

    #: The opacity of the graphic, from 0 to 255.
    opacity: int = attrs.field(default=255)

    # unknown
    blend_type: int = attrs.field(default=0)

    @property
    @override
    def ruby_class_name(self) -> RubySymbol:
        return RPG_EVENT_GRAPHIC

    def __attrs_post_init__(self):
        assert not (self.character_name and self.tile_id), (
            f"Can't have both tile_id '{self.tile_id}' and character_name '{self.character_name}'"
        )


@attrs.define()
@final
class RubyEventPage(RubyUserObject):
    """
    A single event page in an event.
    """

    #: The condition for this event page.
    condition: RubyEventPageCondition = attrs.field()

    #: The graphic for this event page, if any.
    graphic: RubyEventGraphic = attrs.field()

    # unknown?
    move_type: int = attrs.field()
    move_speed: int = attrs.field()
    move_frequency: int = attrs.field()
    move_route: GenericRubyUserObject = attrs.field()

    animate_walk: bool = attrs.field(metadata=ruby_name("walk_anime"))
    animate_step: bool = attrs.field(metadata=ruby_name("step_anime"))

    direction_fix: bool = attrs.field()
    always_on_top: bool = attrs.field()
    trigger: bool = attrs.field()  # wtf is this?
    through: bool = attrs.field()
    commands: list[RubyBaseEventCommand] = attrs.field(metadata=ruby_name("list"))

    @property
    @override
    def ruby_class_name(self) -> RubySymbol:
        return RPG_EVENT_PAGE


@attrs.define()
@final
class RubyRpgEvent(RubyUserObject):
    """
    A single event on a map.

    Events have multiple underlying pages per event which contains all of the data for the event;
    this top-level class only contains a list of pages and the position of the event.
    """

    #: The internal ID of this event.
    id: int = attrs.field()

    #: The editor name of this event.
    name: str = attrs.field()

    #: The X position for this event.
    x: int = attrs.field()
    #: The Y position for this event.
    y: int = attrs.field()

    pages: list[RubyEventPage] = attrs.field()

    @property
    @override
    def ruby_class_name(self) -> RubySymbol:
        return RPG_EVENT
