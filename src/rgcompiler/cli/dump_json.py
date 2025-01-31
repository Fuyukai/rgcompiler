import sys
from pathlib import Path

from rich import print

from rgcompiler.ruby_types import make_reader


def main() -> int:
    try:
        input_file = Path(sys.argv[1])
    except IndexError:
        print(f"usage: {sys.argv[0]} <path to ruby file>")
        return 1

    raw_data = input_file.read_bytes()
    reader = make_reader(raw_data)
    data = reader.next_object()
    print(data)

    return 0
