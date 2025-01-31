import abc
import enum
from collections.abc import Iterable
from typing import NotRequired, TypedDict, cast, final, override

import attrs

type RubyMarshalValue = (
    bool
    | None
    | int
    | str
    | bytes
    | float
    | RubySymbol
    | RubyClass
    | RubySpecialInstance
    | AnyRubyObject
    | list[RubyMarshalValue]
    | dict[RubyMarshalValue, RubyMarshalValue]
)


class RubyExtra(TypedDict):
    """
    Extra data for attrs fields defining how they are marshalled to Ruby fields.
    """

    skip: bool
    ivar_name: NotRequired[str]


def ruby_skip() -> dict[str, RubyExtra]:
    return {"ruby": {"skip": True}}


def ruby_name(name: str) -> dict[str, RubyExtra]:
    return {"ruby": {"skip": False, "ivar_name": name}}


class RubyTypeCode(bytes, enum.Enum):
    """
    An enumeration of the possible Ruby type codes.
    """

    StaticTrue = b"T"
    StaticFalse = b"F"
    StaticNone = b"0"
    Fixnum = b"i"
    Float = b"f"
    Symbol = b":"
    SymbolLink = b";"
    Klass = b"c"
    Object = b"o"
    String = b'"'
    Instance = b"I"
    Array = b"["
    Hash = b"{"
    ObjectLink = b"@"
    UserDefined = b"u"


@attrs.define(slots=True, frozen=True, repr=True, str=False, eq=True, hash=True)
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


def atom(s: str, /) -> RubySymbol:
    """
    Shorthand notation for making a :class:`.RubySymbol`.
    """

    return RubySymbol(s)


@attrs.define(kw_only=True, slots=True, frozen=True)
class RubySpecialInstance:
    """
    An special instance with instance variables.

    This is separate from a :class:`.AnyRubyObject`, and is only used for certain special objects
    under unknown circumstances.
    """

    #: The base object for this instance.
    base_object: RubyMarshalValue = attrs.field()

    #: The additional instance variables for this instance.
    instance_variables: list[tuple[RubySymbol, RubyMarshalValue]] = attrs.field()


class AnyRubyObject(abc.ABC):
    """
    Marker class for any Ruby-side object instance.

    This can be either a :class:`.RubyNonSpecialObject`
    """

    @property
    @abc.abstractmethod
    def ruby_class_name(self) -> RubySymbol:
        """
        The Ruby-side class name for this ruby object.
        """


@attrs.define(kw_only=True, slots=True, frozen=True, eq=True, hash=True)
@final
class RubyClass(AnyRubyObject):
    """
    Wraps a symbol specifically for a Ruby-side class reference.
    """

    #: The name of this class.
    value: RubySymbol = attrs.field()

    @property
    @override
    def ruby_class_name(self) -> RubySymbol:
        """
        The Ruby-side class name for this ruby object.
        """

        return self.value


@attrs.define(kw_only=True, slots=True, frozen=True, eq=True, hash=True)
@final
class RubyModule(AnyRubyObject):
    """
    Wraps a symbol specifically for a Ruby-side module reference.
    """

    #: The name of this class.
    value: RubySymbol = attrs.field()

    @property
    @override
    def ruby_class_name(self) -> RubySymbol:
        """
        The Ruby-side class name for this ruby object.
        """

        return self.value


class RubyNonSpecialObject(AnyRubyObject, abc.ABC):
    """
    Base class for any Ruby object that doesn't have a built-in type code.

    All objects inheriting this are serialisable into a Ruby object (with type code ``o``). This
    should be an ``attrs`` class to function properly; all attrs fields on the class will be
    automatically detected.
    """

    def find_instance_variables(self) -> list[tuple[RubySymbol, RubyMarshalValue]]:
        """
        Finds all of the instance variables on this object for re-serialisation.
        """

        fields: Iterable[attrs.Attribute[RubyMarshalValue]] = attrs.fields(type(self))
        ivars: list[tuple[RubySymbol, RubyMarshalValue]] = []

        for field in fields:
            extra = field.metadata
            name = field.name
            if "ruby" in extra:
                ruby = cast(RubyExtra, extra["ruby"])

                if ruby["skip"]:
                    continue

                name = ruby.get("ivar_name", name)

            if not name.startswith("@"):
                name = "@" + name

            sym = RubySymbol(name)
            ivars.append((sym, getattr(self, field.name)))

        return ivars


@final
@attrs.define(slots=True, kw_only=True)
class GenericRubyObject(RubyNonSpecialObject):
    """
    A generic implementation of :class:`.RubyNonSpecialObject`.

    This class is used when the Ruby deserialiser doesn't understand how to decode an object.
    """

    name: RubySymbol = attrs.field()
    instance_variables: dict[RubySymbol, RubyMarshalValue] = attrs.field()

    @override
    def find_instance_variables(self) -> list[tuple[RubySymbol, RubyMarshalValue]]:
        return list(self.instance_variables.items())

    @property
    @override
    def ruby_class_name(self) -> RubySymbol:
        return self.name

    def get_ivar(self, ivar: RubySymbol | str) -> RubyMarshalValue | None:
        if isinstance(ivar, str):
            ivar = RubySymbol(ivar)

        return self.instance_variables.get(ivar)


def make_generic_object(
    name: RubySymbol, instance_vars: dict[RubySymbol, RubyMarshalValue]
) -> GenericRubyObject:
    """
    Creates a new :class:`.GenericRubyObject`.
    """

    return GenericRubyObject(name=name, instance_variables=instance_vars)


class CustomMarshal(AnyRubyObject, abc.ABC):
    """
    An ABC for any type that has a custom marshal format.

    Examples include the RGSS::Table.
    """

    @abc.abstractmethod
    def get_raw_bytes(self) -> bytes:
        """
        Gets the raw encodeed bytes for this object.
        """


@attrs.define(kw_only=False, slots=True, frozen=True, eq=True, hash=True)
@final
class UnknownUserDefined(CustomMarshal, AnyRubyObject):
    """
    A ruby type that has an unknown deserialisation method.
    """

    #: The class name for this user-defined object.
    name: RubySymbol = attrs.field()

    #: The raw data for this user-defined object.
    raw_data: bytes = attrs.field()

    @property
    @override
    def ruby_class_name(self) -> RubySymbol:
        return self.name

    @override
    def get_raw_bytes(self) -> bytes:
        return self.raw_data
