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
    CheckChoiceCommand,
    ChoiceElseCommand,
    ChoiceEndCommand,
    CommentCommand as CommentCommand,
    ContinuedCommentCommand as ContinuedCommentCommand,
    ContinueDialogueCommand as ContinueDialogueCommand,
    SelectChoiceCommand as SelectChoiceCommand,
    ShowDialogueCommand as ShowDialogueCommand,
)
from rgss.rpg.commands.effects import (
    ChangeScreenColourToneCommand as ChangeScreenColourToneCommand,
    FadeOutBgmCommand,
    PlayBgmCommand,
    PlaySfxCommand as PlaySfxCommand,
    ScreenFlashCommand as ScreenFlashCommand,
    ScrollMapCommand as ScrollMapCommand,
    ShowAnimationCommand,
)
from rgss.rpg.commands.flow import (
    BreakLoopCommand as BreakLoopCommand,
    CheckFacingOpval as CheckFacingOpval,
    CheckSwitchOpval as CheckSwitchOpval,
    CompareVariableOpcode as CompareVariableOpcode,
    CompareVariableToConstantOpval as CompareVariableToConstantOpval,
    CompareVariableToVariableOpval as CompareVariableToVariableOpval,
    ConditionalBranchCommand as ConditionalBranchCommand,
    ElseCommand as ElseCommand,
    EndBranchCommand as EndBranchCommand,
    EnterLoopCommand as EnterLoopCommand,
    ExitEventProcesssingCommand,
    RepeatAboveCommand as RepeatAboveCommand,
)
from rgss.rpg.commands.misc import (
    EmptyCommand as EmptyCommand,
    InlineRubyCommand as InlineRubyCommand,
    InlineRubyContinuedCommand as InlineRubyContinuedCommand,
    SetMoveRouteCommand as SetMoveRouteCommand,
    UnknownCommand as UnknownCommand,
    VisualMoveRouteCommand as VisualMoveRouteCommand,
    WaitCommand as WaitCommand,
    WaitForMoveCompletionCommand as WaitForMoveCompletionCommand,
)
from rgss.rpg.commands.move import (
    CardinalMoveCommand as CardinalMoveCommand,
    ChangeSpeedCommand as ChangeSpeedCommand,
    DiagonalMoveCommand as DiagonalMoveCommand,
    FaceRelativeToPlayerCommand as FaceRelativeToPlayerCommand,
    JumpMoveCommand as JumpMoveCommand,
    SetGraphicMoveCommand as SetGraphicMoveCommand,
    StepOneCommand as StepOneCommand,
    TogglePropertyMoveCommand as TogglePropertyMoveCommand,
    TurnAbsoluteCommand as TurnAbsoluteCommand,
    TurnRandomlyCommand,
)
from rgss.rpg.commands.transfer import (
    SetEventLocationCommand as SetEventLocationCommand,
    TransferPlayerCommand,
)
from rgss.rpg.commands.vars import (
    SetSelfSwitchCommand as SetSelfSwitchCommand,
    SetSwitchCommand as SetSwitchCommand,
    SetVariableCommand as SetVariableCommand,
)
from rhodochrosite.ruby import RubyMarshalValue, RubySymbol

# fmt: off
COMMAND_MAPPING: dict[int, type[RubyBaseCommand]] = {
    1: CardinalMoveCommand,           # Move Down
    2: CardinalMoveCommand,           # Move Left
    3: CardinalMoveCommand,           # Move Right
    4: CardinalMoveCommand,           # Move Up
    5: DiagonalMoveCommand,           # Move Lower Left
    6: DiagonalMoveCommand,           # Move Lower Right
    7: DiagonalMoveCommand,           # Move Upper Left
    8: DiagonalMoveCommand,           # Move Upper Right
    12: StepOneCommand,               # Step Forwards
    13: StepOneCommand,               # Step Backwards
    14: JumpMoveCommand,
    15: WaitCommand,
    16: TurnAbsoluteCommand,          # Turn Down
    17: TurnAbsoluteCommand,          # Turn Left
    18: TurnAbsoluteCommand,          # Turn Right
    19: TurnAbsoluteCommand,          # Turn Up
    24: TurnRandomlyCommand,
    25: FaceRelativeToPlayerCommand,  # Face Player
    26: FaceRelativeToPlayerCommand,  # Face Away From Player
    29: ChangeSpeedCommand,
    31: TogglePropertyMoveCommand,    # Direction Fix On
    32: TogglePropertyMoveCommand,    # Direction Fix Off
    33: TogglePropertyMoveCommand,    # Stop Animation On
    34: TogglePropertyMoveCommand,    # Stop Animation Off
    35: TogglePropertyMoveCommand,    # Move Animation On
    36: TogglePropertyMoveCommand,    # Move Animation Off
    37: TogglePropertyMoveCommand,    # Through On
    38: TogglePropertyMoveCommand,    # Through Off
    39: TogglePropertyMoveCommand,    # Always On Top On
    40: TogglePropertyMoveCommand,    # Always On Top Off
    41: SetGraphicMoveCommand,
    44: PlaySfxCommand,

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
    210: WaitForMoveCompletionCommand,
    402: CheckChoiceCommand,
    403: ChoiceElseCommand,
    404: ChoiceEndCommand,
    242: FadeOutBgmCommand,
    112: EnterLoopCommand,
    113: BreakLoopCommand,
    413: RepeatAboveCommand,
    241: PlayBgmCommand,
    207: ShowAnimationCommand,
    202: SetEventLocationCommand,
    201: TransferPlayerCommand,
    115: ExitEventProcesssingCommand,
}
# fmt: on


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

    klass = COMMAND_MAPPING.get(code)
    if klass is not None:
        result = klass.from_raw_command_and_type(name, raw_cmd)
    else:
        result = UnknownCommand(name=name, raw=raw_cmd)

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
