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
    CallCommonEventCommand,
    CheckFacingOpval as CheckFacingOpval,
    CheckSwitchOpval as CheckSwitchOpval,
    CompareVariableOpcode as CompareVariableOpcode,
    CompareVariableToConstantOpval as CompareVariableToConstantOpval,
    CompareVariableToVariableOpval as CompareVariableToVariableOpval,
    ConditionalBranchCommand as ConditionalBranchCommand,
    ElseCommand as ElseCommand,
    EndBranchCommand as EndBranchCommand,
    EnterLoopCommand as EnterLoopCommand,
    EraseThisEventCommand,
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
    SetOpacityCommand,
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
    # = Move Commands = #
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
    31: TogglePropertyMoveCommand,    # Move Animation On
    32: TogglePropertyMoveCommand,    # Move Animation Off
    33: TogglePropertyMoveCommand,    # Stop Animation On
    34: TogglePropertyMoveCommand,    # Stop Animation Off
    35: TogglePropertyMoveCommand,    # Direction Fix On
    36: TogglePropertyMoveCommand,    # Direction Fix Off
    37: TogglePropertyMoveCommand,    # Through On
    38: TogglePropertyMoveCommand,    # Through Off
    39: TogglePropertyMoveCommand,    # Always On Top On
    40: TogglePropertyMoveCommand,    # Always On Top Off
    41: SetGraphicMoveCommand,
    42: SetOpacityCommand,
    44: PlaySfxCommand,

    # = Event Commands =
    101: ShowDialogueCommand,
    102: SelectChoiceCommand,
    106: WaitCommand,
    108: CommentCommand,
    111: ConditionalBranchCommand,
    112: EnterLoopCommand,
    113: BreakLoopCommand,
    115: ExitEventProcesssingCommand,
    116: EraseThisEventCommand,
    117: CallCommonEventCommand,
    121: SetSwitchCommand,
    122: SetVariableCommand,
    123: SetSelfSwitchCommand,
    201: TransferPlayerCommand,
    202: SetEventLocationCommand,
    203: ScrollMapCommand,
    207: ShowAnimationCommand,
    209: SetMoveRouteCommand,
    210: WaitForMoveCompletionCommand,
    223: ChangeScreenColourToneCommand,
    224: ScreenFlashCommand,
    241: PlayBgmCommand,
    242: FadeOutBgmCommand,
    250: PlaySfxCommand,
    355: InlineRubyCommand,

    # Psuedo-commands. These only exist in relation to another command and can only exist by
    # themselves if the event is corrupted.
    401: ContinueDialogueCommand,
    402: CheckChoiceCommand,
    403: ChoiceElseCommand,
    404: ChoiceEndCommand,
    408: ContinuedCommentCommand,
    411: ElseCommand,
    412: EndBranchCommand,
    413: RepeatAboveCommand,
    509: VisualMoveRouteCommand,
    655: InlineRubyContinuedCommand,
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
