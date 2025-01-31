from __future__ import annotations

from collections.abc import Callable
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
from rhodochrosite.ruby import (
    CustomMarshal,
    RubyClass,
    RubyMarshalValue,
    RubyNonSpecialObject,
    RubySpecialInstance,
    RubySymbol,
    RubyTypeCode,
    UnknownUserDefined,
    make_generic_object,
)

# Unlike Python's ``marshal``, Ruby's ``marshal`` is surprisingly well documented.
# The format is available at https://devdocs.io/ruby~3.3/marshal_rdoc.

ENCODING_SYMBOL = RubySymbol(value="E")

type ObjectMakerFunc = Callable[
    [RubySymbol, dict[RubySymbol, RubyMarshalValue]], RubyNonSpecialObject
]

type CustomMakerFunc = Callable[[RubySymbol, bytes], CustomMarshal]

# Code style note:
# Functions prefixed with `_next` read a type code.
# Functions prefixed with `_read` do not read a type code.


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

    #: A mapping of {ruby type name: (name, instance vars) -> RubyObject} to make user objects.
    object_factories: dict[RubySymbol, ObjectMakerFunc] = attrs.field(factory=dict)

    custom_factories: dict[RubySymbol, CustomMakerFunc] = attrs.field(factory=dict)

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
        # thanks???
        if count == 0:
            return b""

        if data := self.stream.read(count):
            if len(data) < count:
                raise StreamUnexpectedlyEndedError(f"Expected {count} bytes, got {len(data)}")

            return data

        raise StreamUnexpectedlyEndedError(message + f" whilst reading {count} bytes")

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

    def _read_symlink(self) -> RubySymbol:
        """
        Reads a reference to a previous symbol in the stream.
        """

        index = self._read_fixnum()
        try:
            return self.symbol_links[index]
        except IndexError:  # pragma: no cover
            # can't reasonably cover this, Marshal.dump should never do this...?
            raise StreamFormatError(f"Invalid symbol link {index}") from None

    def _read_string(self) -> bytes:
        """
        Reads a raw, un-encoded string from the stream.
        """

        length = self._read_fixnum()
        return self._read(length)

    def _read_array(self) -> list[RubyMarshalValue]:
        """
        Reads a Ruby array.
        """

        item_count = self._read_fixnum()
        return [self.next_object() for _ in range(item_count)]

    def _read_hash(self) -> dict[RubyMarshalValue, RubyMarshalValue]:
        """
        Reads a Ruby hash (dict).
        """

        item_count = self._read_fixnum()
        return {self.next_object(): self.next_object() for _ in range(item_count)}

    def _read_symbol_pairs(self) -> list[tuple[RubySymbol, RubyMarshalValue]]:
        """
        Reads a set of symbol pairs from the stream.
        """

        count = self._read_fixnum()
        pairs: list[tuple[RubySymbol, RubyMarshalValue]] = []

        for _ in range(count):
            name = self.next_object()

            if not isinstance(name, RubySymbol):
                raise InvalidTypeCode(f"Expected a symbol when reading symbol, but got a '{name}'")

            value = self.next_object()

            pairs.append((name, value))

        return pairs

    def _read_instance(self) -> RubySpecialInstance | str | bytes:
        """
        Reads a new "instance" from the stream.

        This will also unwrap str and bytes into their correct types.
        """

        next_code = self._next_type_code()
        completed_object = self._read_object_after_type_code(next_code)
        pairs = self._read_symbol_pairs()

        if self.unwrap_strings and next_code == RubyTypeCode.String and len(pairs) == 1:
            assert isinstance(completed_object, bytes), "string typecode was followed by non-str???"

            name, value = pairs[0]
            assert name == ENCODING_SYMBOL, "expected String to have a single symbol of 'E'"
            if value:
                return completed_object.decode()

            # In practice, I don't think there's any way to produce strings with this set to False.
            return completed_object  # pragma: no cover

        return RubySpecialInstance(base_object=completed_object, instance_variables=pairs)

    def _read_ruby_object(self, name: RubySymbol) -> RubyNonSpecialObject:
        """
        Reads a new Ruby object from the stream.
        """

        pairs = self._read_symbol_pairs()
        maker = self.object_factories.get(name, make_generic_object)
        ivars = dict(pairs)
        return maker(name, ivars)

    def _next_symbol_or_symlink(self) -> RubySymbol:
        """
        Reads either a symbol or a symlink.
        """

        code = self._next_type_code()
        if code == RubyTypeCode.Symbol:
            return self._read_symbol()

        if code == RubyTypeCode.SymbolLink:
            return self._read_symlink()

        raise InvalidTypeCode(f"Expected to read a symbol or symbol link, got a {code} instead")

    def _read_object_after_type_code(self, code: RubyTypeCode) -> RubyMarshalValue:
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
                return self._read_symlink()

            case RubyTypeCode.String:
                # These are possible in the raw stream with e.g. ``Marshal.dump("abc".b)``.
                return self._read_string()

            case RubyTypeCode.Array:
                return self._read_array()

            case RubyTypeCode.Hash:
                return self._read_hash()

            case RubyTypeCode.Klass:  # class
                next = self._read_symbol()
                return RubyClass(value=next)

            case RubyTypeCode.Object:  # regular object
                klass_name = self._next_symbol_or_symlink()
                return self._read_ruby_object(klass_name)

            case RubyTypeCode.UserDefined:
                klass_name = self._next_symbol_or_symlink()
                size = self._read_fixnum()

                factory = self.custom_factories.get(klass_name, UnknownUserDefined)
                return factory(klass_name, self._read(size))

    def next_object(self) -> RubyMarshalValue:
        """
        Reads the next object from this stream.
        """

        return self._read_object_after_type_code(self._next_type_code())


def read_object(data: bytes | bytearray, *, unwrap_strings: bool = True) -> RubyMarshalValue:
    """
    Reads a single ``RubyMarshalValue`` from the provided byte data source.
    """

    return MarshalReader.from_bytes(data, unwrap_strings=unwrap_strings).next_object()
