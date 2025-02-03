from __future__ import annotations

import enum
import struct
from typing import Self, final, override

import attrs

from rhodochrosite.ruby import CustomMarshal, RubySymbol

TABLE_TYPE = RubySymbol("Table")
TONE_TYPE = RubySymbol("Tone")
COLOUR_TYPE = RubySymbol("Color")


@attrs.define(slots=True, kw_only=True)
@final
class RgssTable(CustomMarshal):
    """
    A weird, 3D array table used by certain RGSS files.
    """

    # TODO: validate dimensions

    raw_data: list[int] = attrs.field(factory=list)

    # dimensions of the table; 1 for only rows, 2 for rows + columns, 3 for rows + cols + layers
    dimensions: int = attrs.field()

    row_count: int = attrs.field()
    column_count: int = attrs.field()
    layer_count: int = attrs.field()

    @classmethod
    def make_rgss_table(cls, _: RubySymbol, data: bytes) -> RgssTable:
        header = struct.calcsize("<5L")
        dim, x, y, z, size = struct.unpack("<5L", data[:header])

        if dim == 1:  # pragma: no cover
            assert y == 1, f"only expected 1 column for this table, not {y} columns"
            assert z == 1, f"only expected 1 layer for this table, not {z} layers"

        if dim == 2:  # pragma: no cover
            assert z == 1, f"only expected 1 layer for this table, not {z} layers"

        table_data = data[header:]
        # array of LE shorts
        if len(table_data) // 2 != size:  # pragma: no cover
            # TODO: custom exception
            raise ValueError(f"expected {size} bytes, got {len(data)}")

        raw_data = [i[0] for i in struct.iter_unpack("<H", table_data)]
        return RgssTable(
            raw_data=raw_data, dimensions=dim, row_count=x, column_count=y, layer_count=z
        )

    @property
    @override
    def ruby_class_name(self) -> RubySymbol:
        return TABLE_TYPE

    @override
    def get_raw_bytes(self) -> bytes:
        size = len(self.raw_data)
        header = struct.pack(
            "<5L", self.dimensions, self.row_count, self.column_count, self.layer_count, size
        )

        body = bytearray(header)
        for i in self.raw_data:
            body += struct.pack("<H", i)

        return bytes(body)


# as far as I can tell the only purpose of this being a custom marshal type is to be annoying.
@attrs.define(slots=True, kw_only=True)
class RgssColour(CustomMarshal):
    """
    A RRGGBBAA colour object.
    """

    red: float = attrs.field()
    blue: float = attrs.field()
    green: float = attrs.field()
    alpha: float = attrs.field()

    @classmethod
    def from_bytes(cls, _: RubySymbol, data: bytes) -> Self:
        r, b, g, a = struct.unpack("<4d", data)
        return cls(red=r, blue=b, green=g, alpha=a)

    @property
    @override
    def ruby_class_name(self) -> RubySymbol:
        return COLOUR_TYPE

    @override
    def get_raw_bytes(self) -> bytes:
        return struct.pack("<4d", self.red, self.blue, self.green, self.alpha)


# wtf is the difference?
class RgssTone(RgssColour):
    @property
    @override
    def ruby_class_name(self) -> RubySymbol:
        return TONE_TYPE


class RgssDirection(enum.IntEnum):
    """
    The enumeration of directions used by various RGSS functions.
    """

    # TODO: what are the unk directions? probably diagonals?

    Retain = 0  # Only used by move commands?
    Unk1 = 1
    Down = 2
    Unk3 = 3
    Left = 4
    Unk5 = 5
    Right = 6
    Unk7 = 7
    Up = 8
