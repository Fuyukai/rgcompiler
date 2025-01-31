import sys
from pathlib import Path

from rich import print

from rhodochrosite.reader import read_object


def main() -> int:
    try:
        input_file = Path(sys.argv[1])
    except IndexError:
        print(f"usage: {sys.argv[0]} <path to ruby file>")
        return 1

    raw_data = input_file.read_bytes()
    data = read_object(raw_data)
    print(data)

    return 0
