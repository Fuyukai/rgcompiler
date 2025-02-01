import math
from io import BytesIO
from typing import IO

import attrs

from rhodochrosite.ruby import ENCODING_SYMBOL, RubyMarshalValue, RubySymbol, RubyTypeCode

# Notes: Explicitly doesn't support object links because tracking it would be too annoying.
# Object links suck format wise, too!


@attrs.define(slots=True, kw_only=True)
class MarshalWriter:
    """
    A low-level writer for data in the Ruby marshal format.
    """

    #: The underlying buffer to write to.
    buffer: IO[bytes] = attrs.field(factory=BytesIO)

    #: A mapping of {seen symbols: position} used to emit symbol links.
    seen_symbols: dict[RubySymbol, int] = attrs.field(init=False, factory=dict)

    written_header: bool = attrs.field(init=False, default=False)

    def _write_header(self) -> None:
        if self.written_header:
            return

        self.buffer.write(b"\x04\x08")
        self.written_header = True

    def _write_raw_number(self, number: int) -> None:
        """
        Writes a raw fixed number to the stream.
        """

        # https://github.com/d9pouces/RubyMarshal/blob/81135afa0235ca3b6e895192da3978f49b9a9706/rubymarshal/writer.py#L249

        if number == 0:
            self.buffer.write(b"\x00")
            return

        if 0 < number < 123:
            self.buffer.write((number + 5).to_bytes(length=1, byteorder="little", signed=True))
            return

        if -124 < number < 0:
            self.buffer.write((number - 5).to_bytes(length=1, byteorder="little", signed=True))
            return

        size = int(math.ceil(number.bit_length() / 8.0))
        if size > 5:
            raise ValueError(f"{number} is too big for a fixnum")

        original_obj = number
        factor = 256**size

        if number < 0 and number == -factor:
            size -= 1
            number += factor / 256

        elif number < 0:
            number += factor

        sign = int(math.copysign(size, original_obj))
        self.buffer.write(sign.to_bytes(1, byteorder="little", signed=True))

        for _ in range(size):
            self.buffer.write((number % 256).to_bytes(byteorder="little", signed=False))
            number //= 256

    def _write_raw_string(self, s: str | bytes, /) -> None:
        """
        Writes a single raw bytestring to the stream.
        """

        if isinstance(s, str):
            s = s.encode("utf-8")

        self._write_raw_number(len(s))
        self.buffer.write(s)

    def _write_symbol_with_typecode(self, symbol: RubySymbol) -> None:
        """
        Writes a symbol with the appropriate typecode.
        """

        # we want round-tripping so we have to actually care about writing out symlinks
        try:
            previous_pos = self.seen_symbols[symbol]
        except KeyError:
            pass
        else:
            self.buffer.write(RubyTypeCode.SymbolLink)
            self._write_raw_number(previous_pos)
            return

        self.buffer.write(RubyTypeCode.Symbol)
        self._write_raw_string(symbol.value)
        self.seen_symbols[symbol] = len(self.seen_symbols)

    def _write_pairs(self, pairs: list[tuple[RubyMarshalValue, RubyMarshalValue]]) -> None:
        """
        Writes out a list of (key, value) pairs.
        """

        self._write_raw_number(len(pairs))
        for k, v in pairs:
            self.write_object(k)
            self.write_object(v)

    def _write_array_with_typecode(self, arr: list[RubyMarshalValue]) -> None:
        """
        Writes out an array of objects.
        """

        self.buffer.write(RubyTypeCode.Array)
        self._write_raw_number(len(arr))
        for item in arr:
            self.write_object(item)

    def write_object(self, object: RubyMarshalValue) -> None:
        """
        Writes a single object to the buffer.

        Ideally, this should only be called once at the top-level because ``Marshal.load`` on the
        Ruby side only supports loading a single value.
        """

        self._write_header()

        if object is True:
            self.buffer.write(RubyTypeCode.StaticTrue)
            return

        if object is False:
            self.buffer.write(RubyTypeCode.StaticFalse)
            return

        if object is None:
            self.buffer.write(RubyTypeCode.StaticFalse)

        if isinstance(object, int):
            # TODO: big numbers
            self.buffer.write(RubyTypeCode.Fixnum)
            self._write_raw_number(object)
            return

        if isinstance(object, str):
            # encoded string with instance variables...
            self.buffer.write(RubyTypeCode.Instance)
            self.buffer.write(RubyTypeCode.String)
            self._write_raw_string(object)
            self._write_pairs([(ENCODING_SYMBOL, True)])
            return

        if isinstance(object, bytes):
            # non-encoded string with no instance variables
            self.buffer.write(RubyTypeCode.String)
            self._write_raw_string(object)
            return

        if isinstance(object, RubySymbol):
            self._write_symbol_with_typecode(object)
            return

        if isinstance(object, list):
            self._write_array_with_typecode(object)
            return

        raise NotImplementedError(object)


def write_object(data: RubyMarshalValue) -> bytes:
    buf = BytesIO()
    writer = MarshalWriter(buffer=buf)
    writer.write_object(data)
    return buf.getvalue()
