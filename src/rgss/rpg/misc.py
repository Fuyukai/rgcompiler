from __future__ import annotations

from typing import TYPE_CHECKING, final, override

import attr

if TYPE_CHECKING:
    from lxml.etree import _Element

from lxml.etree import Element

from rhodochrosite.ruby import RubyUserObject, atom

RPG_AUDIOFILE = atom("RPG::AudioFile")


@attr.define(slots=True, kw_only=True)
@final
class RubyAudioFile(RubyUserObject):
    """
    References an audio file in the RPG Maker database.
    """

    #: The name of this file in the database, e.g. ``"Atmosphere- Dark Crystal"``.
    name: str = attr.field()

    #: The volume as a number between 0 to 100, with 0 being silent and 100 being maximum.
    volume: int = attr.field()

    #: The pitch as a number between 0 and 100.
    pitch: int = attr.field()

    def as_tiled_properties(
        self,
        name: str,
        autoplay: bool,
    ) -> _Element:
        """
        Turns this into a custom ``RPG::AudioFile`` property for Tiled maps.
        """

        element = Element("property", name=name, type="class", propertytype=RPG_AUDIOFILE.value)
        props = [
            ("name", self.name),
            ("volume", str(self.volume)),
            ("pitch", str(self.pitch)),
            ("autoplay", str(autoplay)),
        ]
        subprops = Element("properties")

        for prop_name, prop_value in props:
            sub_element = Element("property", name=prop_name, value=prop_value)
            subprops.append(sub_element)

        element.append(subprops)

        return element

    @property
    @override
    def ruby_class_name(self):
        return RPG_AUDIOFILE
