from functools import partial
from typing import Any

from cattrs import Converter
from cattrs.gen import make_dict_unstructure_fn

from rgss.rpg.commands.base import RubyBaseCommand
from rgss.rpg.commands.vars import SvActorRefAttribute
from rgss.rpg.event import RubyEventGraphic, RubyEventPageCondition
from rgss.types import RgssDirection
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


ENUMS_BY_NAME = [
    RgssDirection,
    SvActorRefAttribute,
]


def make_converter() -> Converter:
    """
    Creates a new :class:`cattrs.Converter` that can be used for serialising RGSS objects.
    """

    converter = Converter()

    for enum in ENUMS_BY_NAME:
        converter.register_unstructure_hook(enum, lambda it: it.name)

    converter.register_unstructure_hook(
        RubyEventPageCondition,
        make_dict_unstructure_fn(RubyEventPageCondition, converter, _cattrs_omit_if_default=True),
    )
    converter.register_unstructure_hook(
        RubyEventGraphic,
        make_dict_unstructure_fn(RubyEventGraphic, converter, _cattrs_omit_if_default=True),
    )

    converter.register_unstructure_hook(RubySymbol, partial(unstructure_symbol, converter))
    converter.register_unstructure_hook(RubyBaseCommand, lambda it: it.unstructure(converter))

    converter.register_unstructure_hook(
        GenericRubyUserObject, partial(unstructure_generic_ruby_object, converter)
    )

    return converter


CONVERTER = make_converter()
