from rhodochrosite.writer import write_object


def test_marshal_string() -> None:
    assert write_object("test") == b'\x04\bI"\ttest\x06:\x06ET'
