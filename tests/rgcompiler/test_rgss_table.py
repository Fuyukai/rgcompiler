from pathlib import Path

from rgcompiler.ruby_types import RgssTable

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
