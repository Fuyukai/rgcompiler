from __future__ import annotations

import enum
from typing import Any, cast, final, override

import attrs
from cattrs import Converter

from rgss.rpg.commands.base import RawCommand, RubyBaseEventCommand

# Interesting note: 401/408 are weird, they're only separate to show the text in the editor.
# 101 -> 401 will force scrolling, 101 -> 101 will force a new message.


@attrs.define(kw_only=True)
class ShowDialogueCommand(RubyBaseEventCommand):
    """
    An event command that shows dialogue to the player.
    """

    text: str = attrs.field()

    @classmethod
    @override
    def from_raw_command(cls, cmd: RawCommand) -> ShowDialogueCommand:
        return ShowDialogueCommand(text=cast(str, cmd.parameters[0]), indent=cmd.indent)

    @override
    def to_raw_command(self) -> RawCommand:
        return RawCommand(code=101, parameters=[self.text], indent=self.indent)

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {
            "command": "ShowDialogueCommand",
            "text": self.text,
        }


@attrs.define(kw_only=True)
@final
class ContinueDialogueCommand(ShowDialogueCommand):
    """
    An event command that continues dialogue.
    """

    @classmethod
    @override
    def from_raw_command(cls, cmd: RawCommand) -> ContinueDialogueCommand:
        return ContinueDialogueCommand(text=cast(str, cmd.parameters[0]), indent=cmd.indent)

    @override
    def to_raw_command(self) -> RawCommand:
        return RawCommand(
            code=401,
            parameters=[self.text],
            indent=self.indent,
        )

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {
            "command": "ContinueDialogueCommand",
            "text": self.text,
        }


# not *technically* dialogue, but!


@attrs.define(kw_only=True)
class CommentCommand(RubyBaseEventCommand):
    """
    An event command that is a comment.
    """

    comment: str = attrs.field()

    @classmethod
    @override
    def from_raw_command(cls, cmd: RawCommand) -> CommentCommand:
        return CommentCommand(comment=cast(str, cmd.parameters[0]), indent=cmd.indent)

    @override
    def to_raw_command(self) -> RawCommand:
        return RawCommand(code=108, parameters=[self.comment], indent=self.indent)

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {
            "command": "CommentCommand",
            "comment": self.comment,
        }


@attrs.define(kw_only=True)
@final
class ContinuedCommentCommand(CommentCommand):
    """
    An event command that continues a comment.
    """

    @classmethod
    @override
    def from_raw_command(cls, cmd: RawCommand) -> ContinuedCommentCommand:
        return ContinuedCommentCommand(comment=cast(str, cmd.parameters[0]), indent=cmd.indent)

    @override
    def to_raw_command(self) -> RawCommand:
        return RawCommand(
            code=408,
            parameters=[self.comment],
            indent=self.indent,
        )

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {
            "command": "ContinuedCommentCommand",
            "comment": self.comment,
        }


@final
class ChoiceCancelledAction(enum.IntEnum):
    Disallow = 0
    Choice1 = 1
    Choice2 = 2
    Choice3 = 3
    Choice4 = 4
    Branch = 5


@attrs.define(kw_only=True)
@final
class SelectChoiceCommand(RubyBaseEventCommand):
    """
    An event command that shows a choice to the player.
    """

    choices: list[str] = attrs.field()
    when_cancelled: ChoiceCancelledAction = attrs.field()

    @classmethod
    @override
    def from_raw_command(cls, cmd: RawCommand) -> SelectChoiceCommand:
        return SelectChoiceCommand(
            choices=cast(list[str], cmd.parameters[0]),
            when_cancelled=ChoiceCancelledAction(cmd.parameters[1]),
            indent=cmd.indent,
        )

    @override
    def to_raw_command(self) -> RawCommand:
        return RawCommand(
            code=102,
            parameters=[self.choices, self.when_cancelled.value],
            indent=self.indent,
        )

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {
            "command": "SelectChoiceCommand",
            "choices": self.choices,
            "when_cancelled": self.when_cancelled.name,
        }


@attrs.define(kw_only=True)
@final
class CheckChoiceCommand(RubyBaseEventCommand):
    """
    An event command that will run a block depending on a previous :class:`.SelectChoiceCommand`.
    """

    # not sure why this has both...

    choice_index: int = attrs.field()
    choice_name: str = attrs.field()

    @classmethod
    @override
    def from_raw_command(cls, cmd: RawCommand) -> CheckChoiceCommand:
        return CheckChoiceCommand(
            choice_index=cast(int, cmd.parameters[0]),
            choice_name=cast(str, cmd.parameters[1]),
            indent=cmd.indent,
        )

    @override
    def to_raw_command(self) -> RawCommand:
        return RawCommand(
            code=402,
            parameters=[self.choice_index, self.choice_name],
            indent=self.indent,
        )

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {
            "command": "CheckChoiceCommand",
            "choice_index": self.choice_index,
            "branch_index": self.choice_name,
        }


@attrs.define(kw_only=True)
@final
class ChoiceElseCommand(RubyBaseEventCommand):
    """
    An event command that marks the "cancelled" branch of a choice.
    """

    @classmethod
    @override
    def from_raw_command(cls, cmd: RawCommand) -> ChoiceElseCommand:
        return ChoiceElseCommand(indent=cmd.indent)

    @override
    def to_raw_command(self) -> RawCommand:
        return RawCommand(code=403, indent=self.indent)

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {"command": "ChoiceElseCommand"}


@attrs.define(kw_only=True)
@final
class ChoiceEndCommand(RubyBaseEventCommand):
    """
    An event command that ends a choice block.
    """

    @classmethod
    @override
    def from_raw_command(cls, cmd: RawCommand) -> ChoiceEndCommand:
        return ChoiceEndCommand(indent=cmd.indent)

    @override
    def to_raw_command(self) -> RawCommand:
        return RawCommand(code=404, indent=self.indent)

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {"command": "ChoiceEndCommand"}
