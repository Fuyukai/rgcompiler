from pathlib import Path

import attrs


@attrs.define(kw_only=True)
class RgcProject:
    """
    Contains state about an RGC project.
    """

    #: The path to the project directory for an RGC project.
    project_directory: Path = attrs.field()
