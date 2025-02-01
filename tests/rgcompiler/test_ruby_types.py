import math
from pathlib import Path

from rgcompiler.ruby import read_object_rgxp, write_object_rgxp
from rgcompiler.ruby.rgss import RgssColour, RgssTable

test_data = (Path(__file__).parent / "table.dat").read_bytes()


def test_rgss_table_loading() -> None:
    data = RgssTable.make_rgss_table(None, test_data)  # type: ignore

    assert data.dimensions == 3
    assert data.column_count == 15
    assert data.row_count == 20
    assert data.layer_count == 3


def test_rgss_table_roundtrip() -> None:
    data = RgssTable.make_rgss_table(None, test_data)  # type: ignore
    assert data.get_raw_bytes() == test_data


def test_rgss_color_loading() -> None:
    data = read_object_rgxp(
        b"\x04\bu:\nColor%\x9a\x99\x99\x99\x99\x99\xb9?\x9a\x99\x99\x99\x99\x99\xb9?\x9a\x99\x99\x99\x99\x99\xb9?\x00\x00\x00\x00\x00\x00\x00\x00"
    )
    assert isinstance(data, RgssColour)

    assert math.isclose(data.red, 0.1)
    assert math.isclose(data.blue, 0.1)
    assert math.isclose(data.green, 0.1)
    assert math.isclose(data.alpha, 0)


def test_rgss_color_writing() -> None:
    colour = RgssColour(red=0.39, blue=0.25, green=0.416, alpha=0.77)
    assert (
        write_object_rgxp(colour)
        == b"\x04\bu:\nColor%\xf6(\\\x8f\xc2\xf5\xd8?\x00\x00\x00\x00\x00\x00\xd0?9\xb4\xc8v\xbe\x9f\xda?\xa4p=\n\xd7\xa3\xe8?"  # noqa: E501
    )
