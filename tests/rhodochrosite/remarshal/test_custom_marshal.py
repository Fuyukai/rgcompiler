from rhodochrosite.writer import write_object
from tests.rhodochrosite.unmarshal.test_custom_unmarshal import UserMarshal


def test_writing_custom_marshal_data() -> None:
    assert (
        write_object(UserMarshal([1, 2, 3])) == b"\x04\bu:\x10UserMarshal\x0f\x04\b[\bi\x06i\ai\b"
    )
