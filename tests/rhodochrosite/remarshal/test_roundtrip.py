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
        b'\x04\bI"\x12\xe6\x9a\x81\xe5\xb1\xb1 \xe7\x91\x9e\xe5\xb8\x8c\x06:\x06ET',
    ],
    ids=["abc", "abc-bytestring", "mizuki"],
)
def test_roundtripping_strings(complete_marshal: bytes) -> None:
    loaded = read_object(complete_marshal)
    unloaded = write_object(loaded)
    assert unloaded == complete_marshal


@pytest.mark.parametrize(
    "complete_marshal",
    [
        b"\x04\b[\bi\x06i\ai\b",
        b'\x04\b[\bI"\babc\x06:\x06ETI"\bdef\x06;\x00TI"\bxyz\x06;\x00T',
        b'\x04\b[\bi\x06I"\bdef\x06:\x06ETi\b',
    ],
    ids=["list-int", "list-str", "list-mixed"],
)
def test_roundtripping_arrays(complete_marshal: bytes) -> None:
    loaded = read_object(complete_marshal)
    unloaded = write_object(loaded)
    assert unloaded == complete_marshal


@pytest.mark.parametrize(
    "complete_marshal",
    [
        b'\x04\b{\x06:\tnameI"\babc\x06:\x06ET',
        b"\x04\b{\ti\x06i\ai\bi\ti\ni\vi\fi\r",
        b"\x04\b{\x06i\x06{\x06i\x06i\a"
    ],
    ids=["hash-sym-name", "hash-long-int", "hash-nested"],
)
def test_roundtripping_hashes(complete_marshal: bytes) -> None:
    loaded = read_object(complete_marshal)
    unloaded = write_object(loaded)
    assert unloaded == complete_marshal

    
