# Ruby definition:
# class Test
#   def initialize
#     @abc = 1
#   end
# end

from io import BytesIO
from typing import cast, final, override

from rhodochrosite.reader import MarshalReader, read_object
from rhodochrosite.ruby import GenericRubyObject, RubyMarshalValue, RubyNonSpecialObject, RubySymbol

TEST_NAME = RubySymbol(value="Test")


@final
class _Test(RubyNonSpecialObject):
    def __init__(self, value: int) -> None:
        self.value = value

    @property
    @override
    def ruby_class_name(self) -> RubySymbol:
        return TEST_NAME


def _make_test(name: RubySymbol, args: dict[RubySymbol, RubyMarshalValue]) -> _Test:
    return _Test(value=cast(int, args[RubySymbol(value="@abc")]))


def test_reading_generic_user_object() -> None:
    data = read_object(b"\x04\bo:\tTest\x06:\t@abci\x06")
    assert isinstance(data, GenericRubyObject)
    assert data.name == TEST_NAME
    assert data.find_instance_variables() == [(RubySymbol(value="@abc"), 1)]


def test_reading_custom_user_object() -> None:
    reader = MarshalReader(stream=BytesIO(b"\x04\bo:\tTest\x06:\t@abci\x06"))
    reader.object_factories[TEST_NAME] = _make_test
    next_object = reader.next_object()

    assert isinstance(next_object, _Test)
    assert next_object.value == 1
