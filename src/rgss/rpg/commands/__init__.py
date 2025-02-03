from collections.abc import Callable
from typing import cast

from rgss.rpg.commands.base import (
    CODE_SYMBOL,
    INDENT_SYMBOL,
    PARAMS_SYMBOL,
    RawCommand as RawCommand,
    RubyBaseCommand,
    RubyBaseEventCommand as RubyBaseEventCommand,
)
from rgss.rpg.commands.dialogue import (
    CommentCommand as CommentCommand,
    ContinuedCommentCommand as ContinuedCommentCommand,
    ContinueDialogueCommand as ContinueDialogueCommand,
    SelectChoiceCommand as SelectChoiceCommand,
    ShowDialogueCommand as ShowDialogueCommand,
)
from rgss.rpg.commands.effects import (
    ChangeScreenColourToneCommand as ChangeScreenColourToneCommand,
    PlaySfxCommand as PlaySfxCommand,
    ScreenFlashCommand as ScreenFlashCommand,
    ScrollMapCommand as ScrollMapCommand,
)
from rgss.rpg.commands.misc import (
    EmptyCommand as EmptyCommand,
    InlineRubyCommand as InlineRubyCommand,
    InlineRubyContinuedCommand as InlineRubyContinuedCommand,
    SetMoveRouteCommand as SetMoveRouteCommand,
    UnknownEventCommand as UnknownEventCommand,
    VisualMoveRouteCommand as VisualMoveRouteCommand,
    WaitCommand as WaitCommand,
)
from rgss.rpg.commands.transfer import (
    DirectTransferPlayerCommand as DirectTransferPlayerCommand,
    VariableTransferPlayerCommand as VariableTransferPlayerCommand,
    make_transfer_command,
)
from rgss.rpg.commands.vars import (
    SetSelfSwitchCommand as SetSelfSwitchCommand,
    SetSwitchCommand as SetSwitchCommand,
    SetVariableCommand as SetVariableCommand,
)
from rhodochrosite.ruby import RubyMarshalValue, RubySymbol

COMMAND_MAPPING: dict[int, type[RubyBaseCommand]] = {
    101: ShowDialogueCommand,
    401: ContinueDialogueCommand,
    223: ChangeScreenColourToneCommand,
    106: WaitCommand,
    121: SetSwitchCommand,
    355: InlineRubyCommand,
    655: InlineRubyContinuedCommand,
    108: CommentCommand,
    408: ContinuedCommentCommand,
    224: ScreenFlashCommand,
    250: PlaySfxCommand,
    123: SetSelfSwitchCommand,
    209: SetMoveRouteCommand,
    509: VisualMoveRouteCommand,
    122: SetVariableCommand,
    102: SelectChoiceCommand,
    203: ScrollMapCommand,
}

COMMAND_OVERRIDDES: dict[int, Callable[[RawCommand], RubyBaseCommand]] = {
    201: make_transfer_command,
}


def make_raw_event_command(ivars: dict[RubySymbol, RubyMarshalValue]) -> RawCommand:
    return RawCommand(
        code=cast(int, ivars[CODE_SYMBOL]),
        parameters=cast(list[RubyMarshalValue], ivars[PARAMS_SYMBOL]),
        indent=cast(int, ivars[INDENT_SYMBOL]),
    )


def make_command_from_ivars(
    name: RubySymbol, ivars: dict[RubySymbol, RubyMarshalValue]
) -> RubyBaseCommand:
    code = cast(int, ivars[CODE_SYMBOL])

    if code == 0:
        return EmptyCommand(symbol=name)

    fn = COMMAND_OVERRIDDES.get(
        code, COMMAND_MAPPING.get(code, UnknownEventCommand).from_raw_command
    )
    return fn(make_raw_event_command(ivars))
