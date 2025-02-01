from __future__ import annotations

import struct
from io import BytesIO
from typing import final, override

import attrs

from rhodochrosite.cursor import Cursor
from rhodochrosite.reader import MarshalReader
from rhodochrosite.ruby import CustomMarshal, RubyMarshalValue, RubySymbol
from rhodochrosite.writer import MarshalWriter

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
    def from_bytes(cls, _: RubySymbol, data: bytes) -> RgssColour:
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


def add_all_ruby_types(reader: MarshalReader) -> None:  # pragma: no cover
    """
    Adds all ruby types to the marshal reader.
    """

    reader.custom_factories[TABLE_TYPE] = RgssTable.make_rgss_table
    reader.custom_factories[COLOUR_TYPE] = RgssColour.from_bytes
    reader.custom_factories[TONE_TYPE] = RgssTone.from_bytes


def make_reader(data: bytes) -> MarshalReader:  # pragma: no cover
    reader = MarshalReader(stream=Cursor(wrapped=data), decode_all_strings=True)
    add_all_ruby_types(reader)
    return reader


def read_object_rgxp(data: bytes) -> RubyMarshalValue:  # pragma: no cover
    reader = make_reader(data)
    return reader.next_object()


def write_object_rgxp(data: RubyMarshalValue) -> bytes:  # pragma: no cover
    buf = BytesIO()
    writer = MarshalWriter(buffer=buf)
    writer.write_object(data)
    return buf.getvalue()
