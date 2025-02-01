from rhodochrosite.ruby import atom
from rhodochrosite.writer import write_object


def test_marshal_string() -> None:
    assert write_object("test") == b'\x04\bI"\ttest\x06:\x06ET'


def test_marshal_bytestring() -> None:
    assert write_object(b"test") == b'\x04\b"\ttest'


def test_writing_symbol_links() -> None:
    # official marshaller won't dupe symbols, make sure we don't either
    assert write_object([atom("abc"), atom("abc")]) == b"\x04\b[\a:\babc;\x00"
