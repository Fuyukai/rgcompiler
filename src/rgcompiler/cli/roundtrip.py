import sys
from pathlib import Path

from rgss import read_object_rgxp, write_object_rgxp


def main() -> int:
    try:
        input_file = Path(sys.argv[1])
    except IndexError:
        print(f"usage: {sys.argv[0]} <path to ruby file> [path to output file]")
        return 1

    try:
        output_file = Path(sys.argv[2])
    except IndexError:
        output_file = Path.cwd() / input_file.name

    read_data = read_object_rgxp(input_file.read_bytes())
    written = write_object_rgxp(read_data)

    output_file.write_bytes(written)

    return 0
