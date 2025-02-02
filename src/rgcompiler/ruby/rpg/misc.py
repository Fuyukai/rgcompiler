from typing import final, override

import attr

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

    @property
    @override
    def ruby_class_name(self):
        return RPG_AUDIOFILE
