# ruff: noqa: E221

from typing import final, override

import attrs

from rgss.types import RgssTable
from rhodochrosite.ruby import RubySymbol, RubyUserObject, atom

RPG_TILESET = atom("RPG::Tileset")

# fmt: off
PASSAGE_UP_BLOCKED    = 0b1000
PASSAGE_RIGHT_BLOCKED = 0b0100
PASSAGE_LEFT_BLOCKED  = 0b0010
PASSAGE_DOWN_BLOCKED  = 0b0001
# fmt: on


@attrs.define(kw_only=True, frozen=True, eq=True)
class TilesetTileInfo:
    """
    Information about a single tile in a tileset.
    """

    #: A bitfield containing info about the tileset.
    passage_info: int = attrs.field()

    #: The "priority" of this tile. Not sure what this does.
    priority: int = attrs.field()

    #: The "terrain tag" of this tile. Only used for scripted events.
    terrain_tag: int = attrs.field()

    # for whatever insane reason this is stored inverted, i.e. passable = 0b0, blocked = 0b1
    # wtf, rpg maker?
    @property
    def blocked_upwards(self) -> bool:
        return bool(self.passage_info & PASSAGE_UP_BLOCKED)

    @property
    def blocked_rightwards(self) -> bool:
        return bool(self.passage_info & PASSAGE_RIGHT_BLOCKED)

    @property
    def blocked_leftwards(self) -> bool:
        return bool(self.passage_info & PASSAGE_LEFT_BLOCKED)

    @property
    def blocked_downwards(self) -> bool:
        return bool(self.passage_info & PASSAGE_DOWN_BLOCKED)


@attrs.define(slots=True)
@final
class RubyTileset(RubyUserObject):
    """
    An RGSS tileset object.
    """

    #: The internal name of this tileset.
    name: str = attrs.field()

    #: The internal ID of this tileset.
    id: int = attrs.field()

    #: The name of the graphics file for this tileset.
    tileset_name: str = attrs.field()

    # unknown/undocced/unused fields
    fog_sy: int = attrs.field()
    fog_sx: int = attrs.field()
    fog_hue: int = attrs.field()
    fog_opacity: int = attrs.field()
    fog_zoom: int = attrs.field()
    fog_name: str = attrs.field()
    fog_blend_type: int = attrs.field()

    panorama_name: str = attrs.field()
    panorama_hue: int = attrs.field()

    terrain_tags: RgssTable = attrs.field()
    passages: RgssTable = attrs.field()
    priorities: RgssTable = attrs.field()

    autotile_names: list[str] = attrs.field()

    # for Reborn-style this is entirely unused I think?
    battleback_name: str = attrs.field()

    def get_tile_info(self, tile_idx: int) -> TilesetTileInfo:
        """
        Gets the extended info for a specific tile in this tileset.
        """

        passages = self.passages.raw_data[tile_idx]
        terrain = self.terrain_tags.raw_data[tile_idx]
        priorities = self.priorities.raw_data[tile_idx]

        return TilesetTileInfo(passage_info=passages, priority=priorities, terrain_tag=terrain)

    def __attrs_post_init__(self) -> None:
        assert self.id > 0, f"tileset shouldn't have id {self.id}"

    @property
    @override
    def ruby_class_name(self) -> RubySymbol:
        return RPG_TILESET
