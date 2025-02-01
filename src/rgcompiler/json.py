from functools import partial
from typing import Any

from cattr import Converter

from rhodochrosite.ruby import GenericRubyUserObject, RubySymbol


def unstructure_symbol(converter: Converter, symbol: RubySymbol) -> str:
    return symbol.value


def unstructure_generic_ruby_object(
    converter: Converter,
    gen: GenericRubyUserObject,
) -> Any:
    return {
        "class_name": converter.unstructure(gen.name),
        "instance_vars": {
            converter.unstructure(k): converter.unstructure(v)
            for (k, v) in gen.instance_variables.items()
        },
    }


def make_converter() -> Converter:
    """
    Creates a new :class:`cattrs.Converter` that can be used for serialising RGSS objects.
    """

    converter = Converter()
    converter.register_unstructure_hook(RubySymbol, partial(unstructure_symbol, converter))
    converter.register_unstructure_hook(
        GenericRubyUserObject, partial(unstructure_generic_ruby_object, converter)
    )

    return converter


CONVERTER = make_converter()
