from typing import final, override

import attrs

from rgss.types import RgssTable
from rhodochrosite.ruby import RubySymbol, RubyUserObject, atom

RPG_TILESET = atom("RPG::Tileset")


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

    # TODO: Work out the difference between this and ``name``?
    #: The display name of this tileset.
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

    def __attrs_post_init__(self) -> None:
        assert self.id > 0, f"tileset shouldn't have id {self.id}"

    @property
    @override
    def ruby_class_name(self) -> RubySymbol:
        return RPG_TILESET
