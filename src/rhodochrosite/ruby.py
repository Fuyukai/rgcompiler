import enum
from typing import override

import attrs

type RubyMarshalValue = bool | None | int | str | bytes | RubySymbol | RubySpecialInstance


class RubyTypeCode(bytes, enum.Enum):
    """
    An enumeration of the possible Ruby type codes.
    """

    StaticTrue = b"T"
    StaticFalse = b"F"
    StaticNone = b"0"
    Fixnum = b"i"
    Symbol = b":"
    SymbolLink = b";"
    Klass = b"c"
    Object = b"o"
    String = b'"'
    Instance = b"I"


@attrs.define(kw_only=True, slots=True, frozen=True, repr=True, str=False, eq=True, hash=True)
class RubySymbol:
    """
    A special type of immutable string.

    See https://ruby-doc.org/3.3.3/Symbol.html for more information.
    """

    __match_args__ = ("value",)

    #: The actual value of this symbol.
    #:
    #: Obstensibly, this can be any sequence of bytes; in practice, it's a unicode string.
    value: str = attrs.field()

    @override
    def __str__(self) -> str:
        return self.value


@attrs.define(kw_only=True, slots=True, frozen=True)
class RubySpecialInstance:
    """
    An special instance with instance variables.

    This is separate from a :class:`.RubyObject`!
    """

    #: The base object for this instance.
    base_object: RubyMarshalValue = attrs.field()

    #: The additional instance variables for this instance.
    instance_variables: list[tuple[RubySymbol, RubyMarshalValue]] = attrs.field()
