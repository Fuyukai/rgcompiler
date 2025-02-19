from pathlib import Path

from PIL.Image import Image, open as open_image


def find_image_file_harder(base_path: Path) -> Image:
    """
    Kill all windows users
    """

    paths = [base_path.with_suffix(".png"), base_path.with_suffix(".PNG")]
    for path in paths:
        try:
            return open_image(path)
        except FileNotFoundError:
            continue

    # ok! fuck you!
    for file in base_path.parent.glob("*"):
        if file.is_dir():
            continue

        if file.stem.lower() == base_path.stem.lower():
            return open_image(file)

    raise FileNotFoundError(f"no such PNG image at {base_path}")
