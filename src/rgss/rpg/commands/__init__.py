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
from rgss.rpg.commands.branch import (
    CheckFacingOpval as CheckFacingOpval,
    CheckSwitchOpval as CheckSwitchOpval,
    CompareVariableOpcode as CompareVariableOpcode,
    CompareVariableToConstantOpval as CompareVariableToConstantOpval,
    CompareVariableToVariableOpval as CompareVariableToVariableOpval,
    ConditionalBranchCommand as ConditionalBranchCommand,
    ElseCommand as ElseCommand,
    EndBranchCommand as EndBranchCommand,
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
from rgss.rpg.commands.move import (
    BasicDirectionMoveCommand as BasicDirectionMoveCommand,
    ChangeSpeedCommand,
    StepOneCommand as StepOneCommand,
    ToggleDirectionFixCommand,
    ToggleMoveAnimationCommand,
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

# fmt: off
COMMAND_MAPPING: dict[int, type[RubyBaseCommand]] = {
    1: BasicDirectionMoveCommand,
    2: BasicDirectionMoveCommand,
    3: BasicDirectionMoveCommand,
    4: BasicDirectionMoveCommand,
    12: StepOneCommand,
    13: StepOneCommand,
    31: ToggleMoveAnimationCommand,
    32: ToggleMoveAnimationCommand,
    35: ToggleDirectionFixCommand,
    36: ToggleDirectionFixCommand,
    29: ChangeSpeedCommand,

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
    111: ConditionalBranchCommand,
    411: ElseCommand,
    412: EndBranchCommand,
}
# fmt: on

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
    raw_cmd = make_raw_event_command(ivars)
    code = raw_cmd.code

    if code == 0:
        return EmptyCommand(symbol=name, raw=raw_cmd)

    fn = COMMAND_OVERRIDDES.get(code)
    if fn is None:
        klass = COMMAND_MAPPING.get(code)
        if klass is not None:
            fn = klass.from_raw_command

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
