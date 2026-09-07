import importlib.metadata
from pathlib import Path

import rich_click as click

version = importlib.metadata.version("rgcompiler")


@click.group()
@click.version_option(version)
def main() -> None:
    """
    rgcompiler - a CLI toolkit for RPG Maker XP projects.
    """

    # raise NotImplementedError(
    #    "https://tenor.com/view/bang-dream-bandori-mygo-its-mygo-anon-gif-12590567651299396850"
    # )


@main.command()
@click.argument(
    "input_directory",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    required=True,
)
@click.argument(
    "output_directory",
    type=click.Path(file_okay=False, path_type=Path),
    required=True,
)
@click.option(
    "--flat-map-generation",
    is_flag=True,
    help="Flattens the output map directories instead of making them a hierachy.",
    default=False,
    show_default=True,
)
def decompile(
    input_directory: Path, output_directory: Path, flat_map_generation: bool = False
) -> None:
    """
    Imports and decompiles an existing RPG Maker XP project.
    """


if __name__ == "__main__":
    main()
