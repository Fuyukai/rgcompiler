from typing import cast

from rgss.rpg.commands.base import (
    CODE_SYMBOL,
    INDENT_SYMBOL,
    PARAMS_SYMBOL,
    RPG_EVENT_COMMAND,
    RPG_MOVE_COMMAND,
    RawCommand as RawCommand,
    RubyBaseCommand as RubyBaseCommand,
    RubyBaseEventCommand as RubyBaseEventCommand,
    RubyBaseMoveCommand as RubyBaseMoveCommand,
)
from rgss.rpg.commands.dialogue import (
    CheckChoiceCommand as CheckChoiceCommand,
    ChoiceElseCommand as ChoiceElseCommand,
    ChoiceEndCommand as ChoiceEndCommand,
    CommentCommand as CommentCommand,
    ContinuedCommentCommand as ContinuedCommentCommand,
    ContinueDialogueCommand as ContinueDialogueCommand,
    SelectChoiceCommand as SelectChoiceCommand,
    ShowDialogueCommand as ShowDialogueCommand,
)
from rgss.rpg.commands.effects import (
    ChangeBattleBgmCommand as ChangeBattleBgmCommand,
    ChangeFogOpacityCommand as ChangeFogOpacityCommand,
    ChangeScreenColourToneCommand as ChangeScreenColourToneCommand,
    FadeOutBgmCommand as FadeOutBgmCommand,
    PlayBgmCommand as PlayBgmCommand,
    PlaySfxCommand as PlaySfxCommand,
    ScreenFlashCommand as ScreenFlashCommand,
    ScreenShakeCommand as ScreenShakeCommand,
    ScrollMapCommand as ScrollMapCommand,
    SetTransparencyFlagCommand as SetTransparencyFlagCommand,
    ShowAnimationCommand as ShowAnimationCommand,
    ShowPictureCommand as ShowPictureCommand,
)
from rgss.rpg.commands.flow import (
    BreakLoopCommand as BreakLoopCommand,
    CallCommonEventCommand as CallCommonEventCommand,
    CheckFacingOpval as CheckFacingOpval,
    CheckSwitchOpval as CheckSwitchOpval,
    CompareVariableOpcode as CompareVariableOpcode,
    CompareVariableToConstantOpval as CompareVariableToConstantOpval,
    CompareVariableToVariableOpval as CompareVariableToVariableOpval,
    ConditionalBranchCommand as ConditionalBranchCommand,
    DefineLabelEventCommand as DefineLabelEventCommand,
    ElseCommand as ElseCommand,
    EndBranchCommand as EndBranchCommand,
    EnterLoopCommand as EnterLoopCommand,
    EraseThisEventCommand as EraseThisEventCommand,
    ExitEventProcesssingCommand as ExitEventProcesssingCommand,
    JumpToLabelEventCommand as JumpToLabelEventCommand,
    RepeatAboveCommand as RepeatAboveCommand,
)
from rgss.rpg.commands.misc import (
    ChangeMapSettingsCommand as ChangeMapSettingsCommand,
    EmptyCommand as EmptyCommand,
    InlineRubyCommand as InlineRubyCommand,
    InlineRubyContinuedCommand as InlineRubyContinuedCommand,
    MemoriseBgmCommand as MemoriseBgmCommand,
    RecoverAllCommand as RecoverAllCommand,
    SetMoneyCommand as SetMoneyCommand,
    SetMoveRouteCommand as SetMoveRouteCommand,
    UnknownCommand as UnknownCommand,
    VisualMoveRouteCommand as VisualMoveRouteCommand,
    WaitCommand as WaitCommand,
    WaitForMoveCompletionCommand as WaitForMoveCompletionCommand,
)
from rgss.rpg.commands.move import (
    CardinalMoveCommand as CardinalMoveCommand,
    ChangeFrequencyCommand as ChangeFrequencyCommand,
    ChangeSpeedCommand as ChangeSpeedCommand,
    DiagonalMoveCommand as DiagonalMoveCommand,
    FaceRelativeToPlayerCommand as FaceRelativeToPlayerCommand,
    JumpMoveCommand as JumpMoveCommand,
    MoveRelativeToPlayerCommand as MoveRelativeToPlayerCommand,
    SetBlendingMoveCommand as SetBlendingMoveCommand,
    SetGraphicMoveCommand as SetGraphicMoveCommand,
    SetOpacityCommand as SetOpacityCommand,
    StepOneCommand as StepOneCommand,
    TogglePropertyMoveCommand as TogglePropertyMoveCommand,
    TurnAbsoluteCommand as TurnAbsoluteCommand,
    TurnRandomlyCommand as TurnRandomlyCommand,
    TurnRelativeCommand as TurnRelativeCommand,
)
from rgss.rpg.commands.transfer import (
    SetEventLocationCommand as SetEventLocationCommand,
    TransferPlayerCommand as TransferPlayerCommand,
)
from rgss.rpg.commands.vars import (
    InputNumberCommand as InputNumberCommand,
    SetSelfSwitchCommand as SetSelfSwitchCommand,
    SetSwitchCommand as SetSwitchCommand,
    SetVariableCommand as SetVariableCommand,
    WaitForButtonPressCommand as WaitForButtonPressCommand,
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
    10: MoveRelativeToPlayerCommand,  # Move Towards Player
    11: MoveRelativeToPlayerCommand,  # Move Away From Player
    12: StepOneCommand,               # Step Forwards
    13: StepOneCommand,               # Step Backwards
    14: JumpMoveCommand,
    15: WaitCommand,
    16: TurnAbsoluteCommand,          # Turn Down
    17: TurnAbsoluteCommand,          # Turn Left
    18: TurnAbsoluteCommand,          # Turn Right
    19: TurnAbsoluteCommand,          # Turn Up
    20: TurnRelativeCommand,          # Turn 90° Right
    21: TurnRelativeCommand,          # Turn 90° Left
    22: TurnRelativeCommand,          # Turn 180°
    24: TurnRandomlyCommand,
    25: FaceRelativeToPlayerCommand,  # Face Player
    26: FaceRelativeToPlayerCommand,  # Face Away From Player
    27: SetSwitchCommand,             # Switch On
    28: SetSwitchCommand,             # Switch Off
    29: ChangeSpeedCommand,
    30: ChangeFrequencyCommand,
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
    43: SetBlendingMoveCommand,
    44: PlaySfxCommand,

    # = Event Commands = #
    101: ShowDialogueCommand,
    102: SelectChoiceCommand,
    103: InputNumberCommand,
    105: WaitForButtonPressCommand,
    106: WaitCommand,
    108: CommentCommand,
    111: ConditionalBranchCommand,
    112: EnterLoopCommand,
    113: BreakLoopCommand,
    115: ExitEventProcesssingCommand,
    116: EraseThisEventCommand,
    117: CallCommonEventCommand,
    118: DefineLabelEventCommand,
    119: JumpToLabelEventCommand,
    121: SetSwitchCommand,
    122: SetVariableCommand,
    123: SetSelfSwitchCommand,
    125: SetMoneyCommand,
    132: ChangeBattleBgmCommand,
    201: TransferPlayerCommand,
    202: SetEventLocationCommand,
    203: ScrollMapCommand,
    204: ChangeMapSettingsCommand,
    206: ChangeFogOpacityCommand,
    207: ShowAnimationCommand,
    208: SetTransparencyFlagCommand,
    209: SetMoveRouteCommand,
    210: WaitForMoveCompletionCommand,
    223: ChangeScreenColourToneCommand,
    224: ScreenFlashCommand,
    225: ScreenShakeCommand,
    231: ShowPictureCommand,
    241: PlayBgmCommand,
    242: FadeOutBgmCommand,
    247: MemoriseBgmCommand,
    249: PlayBgmCommand,  # For "ME"s,
    250: PlaySfxCommand,
    314: RecoverAllCommand,
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
