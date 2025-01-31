import pytest

from rhodochrosite.reader import read_object
from rhodochrosite.writer import write_object


@pytest.mark.parametrize(
    "complete_marshal",
    [
        b"\x04\bi\x00",
        b"\x04\bi,",
        b"\x04\bi\xd4",
        b"\x04\bi\x02c\x0f",
        b"\x04\bi\xfe\x9d\xf0",
        b"\x04\bi\x03\xd3\x02\x06",
        b"\x04\bi\xfd-\xfd\xf9",
        b"\x04\bi\x04\x93\x1aY\x02",
        b"\x04\bi\xfcm\xe5\xa6\xfd",
    ],
    ids=[
        "zero",
        "basic-39",
        "basic-neg-39",
        "2byte-39",
        "2byte-neg-39",
        "3byte-39",
        "3byte-neg39",
        "4byte-39",
        "4byte-neg39",
    ],
)
def test_roundtripping_ints(complete_marshal: bytes) -> None:
    loaded = read_object(complete_marshal)
    unloaded = write_object(loaded)
    assert unloaded == complete_marshal

@pytest.mark.parametrize("value", [0, 39, -39, 3939, -3939, 393939, -393939, 39393939, -39393939])
def test_reverse_roundtrip_int(value: int) -> None:
    written = write_object(value)
    assert read_object(written) == value

@pytest.mark.parametrize(
    "complete_marshal",
    [
        b'\x04\bI"\babc\x06:\x06ET',
        b'\x04\b"\babc',
        b'\x04\bI"\x12\xE6\x9A\x81\xE5\xB1\xB1 \xE7\x91\x9E\xE5\xB8\x8C\x06:\x06ET'
    ],
    ids=["abc", "abc-bytestring", "mizuki"]
)
def test_roundtripping_strings(complete_marshal: bytes) -> None:
    loaded = read_object(complete_marshal)
    unloaded = write_object(loaded)
    assert unloaded == complete_marshal
