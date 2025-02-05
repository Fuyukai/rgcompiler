import sys
import time
from collections import Counter, defaultdict
from collections.abc import Iterable
from pathlib import Path

import rich
import rich.progress
from rich import print

from rgss import read_object_rgxp
from rgss.rpg.commands.base import RubyBaseCommand
from rgss.rpg.commands.misc import SetMoveRouteCommand, UnknownCommand
from rgss.rpg.map import RubyRpgMap

total = 0
failed = 0

found_unknown: dict[str, Counter[int]] = defaultdict(Counter)
actual_errors: dict[str, Exception] = {}


def _check_commands(map_name: str, event_name: str, commands: Iterable[RubyBaseCommand]):
    global total, failed

    for command in commands:
        total += 1
        if isinstance(command, SetMoveRouteCommand):
            _check_commands(map_name, event_name, command.move_route.moves)
            continue

        if isinstance(command, UnknownCommand):
            raw = command.to_raw_command()
            print(f"[yellow]found unknown command[/yellow] {raw.code} ({command.ruby_class_name})")
            print(f" in map: [cyan]{map_name}[/cyan] event: [cyan]{event_name}[/cyan]")
            found_unknown[map_name][raw.code] += 1
            failed += 1


def main():
    map_path = Path(sys.argv[1])
    maps = map_path.glob("Map*.rxdata")

    before = time.monotonic()

    for map in rich.progress.track(list(maps), description="loading maps..."):
        if map.name == "MapInfos.rxdata":
            continue

        print(f"[cyan]loading map:[/cyan] {map.name}")
        data = map.read_bytes()
        try:
            loaded = read_object_rgxp(data)
        except Exception as e:
            print(f"[red]map load failed![/red] {e}")
            actual_errors[map.name] = e
            continue

        assert isinstance(loaded, RubyRpgMap)
        print("[green]map loaded![/green] verifying event coverage...")

        for event in loaded.events.values():
            for page in event.pages:
                _check_commands(map.name, event.name, page.move_route.moves)
                _check_commands(map.name, event.name, page.commands)

    after = time.monotonic()

    print(f"checked all maps in {after - before:.2f} seconds!")
    print()
    print(f"total events: [pink]{total}[/pink], failed: [red]{failed}[/red]")
    print(f"success rate: [green]{(total - failed) / total * 100:.2f}%[/green]")
    print("unknown commands:")

    for map in found_unknown:
        print(f"map: [cyan]{map}[/cyan]")
        for code, count in found_unknown[map].most_common():
            print(f"  code: {code}, count: {count}")

    print()
    print("actual errors:")
    print(actual_errors)


if __name__ == "__main__":
    main()
