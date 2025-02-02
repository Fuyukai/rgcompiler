import json
import sys
from pathlib import Path

from rich import print as r_print

from rgcompiler.json import CONVERTER
from rgcompiler.ruby import make_reader


def main() -> int:
    try:
        input_file = Path(sys.argv[1])
    except IndexError:
        print(f"usage: {sys.argv[0]} <path to ruby file>")
        return 1

    raw_data = input_file.read_bytes()
    reader = make_reader(raw_data)
    data = reader.next_object()

    result = json.dumps(CONVERTER.unstructure(data), indent=4)

    if sys.stdout.isatty():
        r_print(result)
    else:
        print(result)

    return 0
