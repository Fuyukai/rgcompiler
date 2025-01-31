from __future__ import annotations

from io import BytesIO
from types import TracebackType
from typing import IO

import attrs

from rhodochrosite.exc import (
    InvalidTypeCode,
    NotAMarshalFile,
    StreamFormatError,
    StreamUnexpectedlyEndedError,
)
from rhodochrosite.ruby import RubyMarshalValue, RubySpecialInstance, RubySymbol, RubyTypeCode

# Unlike Python's ``marshal``, Ruby's ``marshal`` is surprisingly well documented.
# The format is available at https://devdocs.io/ruby~3.3/marshal_rdoc.

ENCODING_SYMBOL = RubySymbol(value="E")


@attrs.define(slots=True, kw_only=True)
class MarshalReader:
    """
    A low-level reader for data in the Ruby marshal format.
    """

    #: The stream of data to read. This is a file-like object that returns raw binary data.
    #:
    #: For in-memory streams, use a :class:`io.BytesIO`.
    stream: IO[bytes] = attrs.field()

    #: A list of previously encountered symbols in this stream.
    symbol_links: list[RubySymbol] = attrs.field(init=False, factory=list)

    #: If True, then strings will be unwrapped in the stream.
    unwrap_strings: bool = attrs.field(default=True)

    @classmethod
    def from_bytes(cls, data: bytes | bytearray, *, unwrap_strings: bool = True) -> MarshalReader:
        """
        Creates a new :class:`.MarshalReader` from a series of bytes.
        """

        return MarshalReader(stream=BytesIO(data), unwrap_strings=unwrap_strings)

    def __attrs_post_init__(self) -> None:
        # e first two bytes of the stream contain the major and minor version, each as a single byte
        # encoding a digit. The version implemented in Ruby is 4.8 (stored as “x04x08”) and is
        # supported by ruby 1.8.0 and newer.

        magic_number = self.stream.read(2)
        if magic_number != b"\x04\x08":
            raise NotAMarshalFile(f"Invalid magic number {magic_number}")

    def _read(self, count: int, /, message: str = "End of file") -> bytes:
        if data := self.stream.read(count):
            if len(data) < count:
                raise StreamUnexpectedlyEndedError(f"Expected {count} bytes, got {len(data)}")

            return data

        raise StreamUnexpectedlyEndedError(message)

    def __enter__(self) -> IO[bytes]:  # pragma: no cover
        return self.stream.__enter__()

    def __exit__(
        self,
        type: type[BaseException] | None,
        value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:  # pragma: no cover
        return self.stream.__exit__(type, value, traceback)

    def _next_type_code(self) -> RubyTypeCode:
        """
        Reads the next type code from the stream.

        A type code is a single character identifying the next object in the stream.
        """

        return RubyTypeCode(self._read(1, "EOF reached when reading next object type code"))

    # stolen from rubymarshal directly
    def _read_fixnum(self) -> int:
        size_byte = self._read(1, "Missing the size byte for a fixnum")

        # hardcoded zero
        if size_byte == b"\x00":
            return 0

        length = int.from_bytes(size_byte, signed=True)

        if 5 < length < 128:
            return length - 5

        if -129 < length < -5:
            return length + 5

        result = 0
        factor = 1

        int_body = self._read(abs(length), f"Missing fixnum value of length {abs(length)}")

        for byte in int_body:
            result += byte * factor
            factor *= 256

        if length < 0:
            result = result - factor

        return result

    def _read_symbol(self) -> RubySymbol:
        size = self._read_fixnum()
        name = self._read(size, f"Missing symbol body of length {size}")

        symbol = RubySymbol(value=name.decode(encoding="utf-8"))
        self.symbol_links.append(symbol)
        return symbol

    def _read_string(self) -> bytes:
        """
        Reads a raw, un-encoded string from the stream.
        """

        length = self._read_fixnum()
        return self._read(length)

    def _read_instance(self) -> RubySpecialInstance | str | bytes:
        """
        Reads a new "instance" from the stream. This will also unwrap str and bytes into their
        correct types.
        """

        next_code = self._next_type_code()
        completed_object = self._next_object_after_type_code(next_code)
        count = self._read_fixnum()
        pairs: list[tuple[RubySymbol, RubyMarshalValue]] = []

        for _ in range(count):
            name = self.next_object()
            assert isinstance(name, RubySymbol), f"Expected a symbol, but got a '{name}'"
            value = self.next_object()

            pairs.append((name, value))

        if self.unwrap_strings and next_code == RubyTypeCode.String and len(pairs) == 1:
            assert isinstance(completed_object, bytes), "string typecode was followed by non-str???"

            name, value = pairs[0]
            assert name == ENCODING_SYMBOL, "expected String to have a single symbol of 'E'"
            if value:
                return completed_object.decode()

            # In practice, I don't think there's any way to produce strings with this set to False.
            return completed_object  # pragma: no cover

        return RubySpecialInstance(base_object=completed_object, instance_variables=pairs)

    def _next_object_after_type_code(self, code: RubyTypeCode) -> RubyMarshalValue:
        """
        Reads the next object from the stream using the provided type code.
        """

        match code:
            case RubyTypeCode.Instance:
                return self._read_instance()

            case RubyTypeCode.StaticTrue:
                return True

            case RubyTypeCode.StaticFalse:
                return False

            case RubyTypeCode.StaticNone:
                return None

            case RubyTypeCode.Fixnum:  # *not* the arbitrary big-integer type
                return self._read_fixnum()

            case RubyTypeCode.Symbol:
                return self._read_symbol()

            case RubyTypeCode.SymbolLink:
                index = self._read_fixnum()
                try:
                    return self.symbol_links[index]
                except IndexError:  # pragma: no cover
                    # can't reasonably cover this, Marshal.dump should never do this...?
                    raise StreamFormatError(f"Invalid symbol link {index}") from None

            case RubyTypeCode.String:
                # These are possible in the raw stream with e.g. ``Marshal.dump("abc".b)``.
                return self._read_string()

            case RubyTypeCode.Klass:  # class
                next = self._read_symbol()
                print(next)
                raise InvalidTypeCode(b"c")

            case RubyTypeCode.Object:  # regular object
                klass_name = self.next_object()
                print(klass_name)
                raise InvalidTypeCode(b"o")

    def next_object(self) -> RubyMarshalValue:
        """
        Reads the next object from this stream.
        """

        return self._next_object_after_type_code(self._next_type_code())


def read_object(data: bytes | bytearray, *, unwrap_strings: bool = True) -> RubyMarshalValue:
    """
    Reads a single ``RubyMarshalValue`` from the provided byte data source.
    """

    return MarshalReader.from_bytes(data, unwrap_strings=unwrap_strings).next_object()
