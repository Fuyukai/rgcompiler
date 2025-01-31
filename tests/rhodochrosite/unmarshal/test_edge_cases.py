import pytest

from rhodochrosite.reader import read_object
from rhodochrosite.ruby import GenericRubyObject, RubyMarshalValue, RubySymbol


def test_reading_zero_size() -> None:
    assert read_object(b'\x04\bI"\x00\x06:\x06ET') == ""


def test_reading_invalid_size() -> None:
    with pytest.raises(EOFError):
        read_object(b'\x04\bI"\x00\x07:\x06ET')


def test_object_with_symlink_name() -> None:
    result: list[RubyMarshalValue] = read_object(b"\x04\b[\a:\tTesto;\x00\x00") # type: ignore
    
    assert result[0] == RubySymbol("Test")
    obb = result[1]
    assert isinstance(obb, GenericRubyObject)
    assert obb.name == result[0]

