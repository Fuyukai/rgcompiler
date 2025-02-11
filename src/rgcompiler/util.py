from pathlib import Path

from PIL.Image import Image, open as open_image


def clamp_downwards(num: int, mult: int) -> int:
    """
    Clamps the provided number downwards towards the provided mult.
    """

    return (num // mult) * mult


def find_image(base_path: Path) -> Image:
    paths = [base_path.with_suffix(".png"), base_path.with_suffix(".PNG")]
    for path in paths:
        try:
            return open_image(path)
        except FileNotFoundError:
            continue

    raise FileNotFoundError(f"no such PNG image at {base_path}")
