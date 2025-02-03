from collections.abc import Callable
from typing import cast

from rgss.rpg.commands.base import (
    CODE_SYMBOL,
    INDENT_SYMBOL,
    PARAMS_SYMBOL,
    RPG_EVENT_COMMAND,
    RPG_MOVE_COMMAND,
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
    UnknownCommand as UnknownCommand,
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
        indent=cast(int, ivars.get(INDENT_SYMBOL, 0)),
    )


def make_command_from_ivars(
    name: RubySymbol, ivars: dict[RubySymbol, RubyMarshalValue]
) -> RubyBaseCommand:
    code = cast(int, ivars[CODE_SYMBOL])

    if code == 0:
        return EmptyCommand(symbol=name)

    fn = COMMAND_OVERRIDDES.get(code)
    if fn is None:
        klass = COMMAND_MAPPING.get(code)
        if klass is not None:
            fn = klass.from_raw_command

    raw_cmd = make_raw_event_command(ivars)

    if fn is None:  # noqa: SIM108
        result = UnknownCommand(name=name, raw=raw_cmd)
    else:
        result = fn(raw_cmd)

    if __debug__:
        if code < 100:
            assert result.ruby_class_name == RPG_MOVE_COMMAND, (
                f"expected a move command with code {code}, got {result}"
            )
        else:
            assert result.ruby_class_name == RPG_EVENT_COMMAND, (
                f"expected an event command with code {code}"
            )

    return result
