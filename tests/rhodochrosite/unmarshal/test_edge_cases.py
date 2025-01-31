import pytest

from rhodochrosite.reader import read_object


def test_reading_zero_size() -> None:
    assert read_object(b'\x04\bI"\x00\x06:\x06ET') == ""


def test_reading_invalid_size() -> None:
    with pytest.raises(EOFError):
        read_object(b'\x04\bI"\x00\x07:\x06ET')
