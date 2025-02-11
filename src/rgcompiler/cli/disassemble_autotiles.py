import itertools
import sys

from PIL import Image

TILE_SIZE = 16
OUTPUT_WIDTH = 8
OUTPUT_HEIGHT = 6

# fmt: off
TILE_MAPPING = [
    [26, 27, 32, 33], [4, 27, 32, 33], [26, 5, 32, 33], [4, 5, 32, 33], [26, 27, 32, 11], [4, 27, 32, 11], [26, 5, 32, 11], [4, 5, 32, 11],  # noqa: E501
    [26, 27, 10, 33], [4, 27, 10, 33], [26, 5, 10, 33], [4, 5, 10, 33], [26, 27, 10, 11], [4, 27, 10, 11], [26, 5, 10, 11], [4, 5, 10, 11],  # noqa: E501
    [24, 25, 30, 31], [24, 5, 30, 31], [24, 25, 30, 31], [24, 5, 30, 11], [14, 15, 20, 21], [14, 15, 20, 11], [14, 15, 10, 21], [14, 15, 10, 11],  # noqa: E501
    [28, 29, 34, 35], [28, 29, 10, 35], [4, 29, 34, 35], [4, 29, 10, 35], [38, 39, 44, 45], [4, 39, 44, 45], [38, 5, 44, 45], [4, 5, 44, 45],  # noqa: E501
    [24, 29, 30, 35], [14, 15, 44, 45], [12, 13, 18, 19], [12, 13, 18, 11], [16, 17, 22, 23], [16, 17, 10, 23], [40, 41, 46, 47], [4, 41, 46, 47],  # noqa: E501
    [36, 37, 42, 43], [36, 5, 42, 43], [12, 17, 18, 23], [12, 13, 42, 43], [36, 41, 42, 47], [17, 17, 46, 47], [12, 13, 42, 47], [0, 1, 6, 7],  # noqa: E501
]
# fmt: on


def main():
    tileset = Image.open(sys.argv[1])
    tileset = tileset.convert("RGBA")
    parts: list[Image.Image] = []

    for y in range(0, 128, TILE_SIZE):
        for x in range(0, 96, TILE_SIZE):
            bounding_box = (x, y, x + TILE_SIZE, y + TILE_SIZE)
            parts.append(tileset.crop(bounding_box))

    out_image = Image.new(
        mode=tileset.mode, size=(2 * OUTPUT_WIDTH * TILE_SIZE, 2 * OUTPUT_HEIGHT * TILE_SIZE)
    )

    for y, row in enumerate(itertools.batched(TILE_MAPPING, OUTPUT_WIDTH, strict=True)):
        for x, square in enumerate(row):
            for i, part in enumerate(square):
                dy, dx = divmod(i, 2)
                box = ((2 * x + dx) * TILE_SIZE, (2 * y + dy) * TILE_SIZE)
                out_image.paste(parts[part], box=box)

    out_image.save(sys.argv[2])


if __name__ == "__main__":
    main()
