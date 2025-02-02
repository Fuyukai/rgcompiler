from typing import cast

from rgss.rpg.commands.base import (
    CODE_SYMBOL,
    INDENT_SYMBOL,
    PARAMS_SYMBOL,
    RawEventCommand as RawEventCommand,
    RubyBaseEventCommand as RubyBaseEventCommand,
)
from rgss.rpg.commands.dialogue import (
    ContinueDialogueCommand as ContinueDialogueCommand,
    ShowDialogueCommand as ShowDialogueCommand,
)
from rgss.rpg.commands.misc import (
    ChangeScreenColourToneCommand as ChangeScreenColourToneCommand,
    EmptyEventCommand as EmptyEventCommand,
    UnknownEventCommand as UnknownEventCommand,
    WaitCommand as WaitCommand,
)
from rhodochrosite.ruby import RubyMarshalValue, RubySymbol

COMMAND_MAPPING: dict[int, type[RubyBaseEventCommand]] = {
    0: EmptyEventCommand,
    101: ShowDialogueCommand,
    401: ContinueDialogueCommand,
    223: ChangeScreenColourToneCommand,
    106: WaitCommand,
}


def make_event_command_from_ivars(
    _: RubySymbol, ivars: dict[RubySymbol, RubyMarshalValue]
) -> RubyBaseEventCommand:
    code = cast(int, ivars[CODE_SYMBOL])
    return COMMAND_MAPPING.get(code, UnknownEventCommand).from_raw_event_command(
        RawEventCommand(
            code=code,
            parameters=cast(list[RubyMarshalValue], ivars[PARAMS_SYMBOL]),
            indent=cast(int, ivars[INDENT_SYMBOL]),
        )
    )
