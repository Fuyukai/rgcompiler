from __future__ import annotations

import enum
from typing import Any, cast, override

import attrs
from cattr import Converter

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
        return ShowDialogueCommand(text=cast(str, cmd.parameters[0]))

    @override
    def to_raw_command(self) -> RawCommand:
        return RawCommand(
            code=101,
            parameters=[self.text],
        )

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {
            "command": "ShowDialogueCommand",
            "text": self.text,
        }


@attrs.define(kw_only=True)
class ContinueDialogueCommand(ShowDialogueCommand):
    """
    An event command that continues dialogue.
    """

    @classmethod
    @override
    def from_raw_command(cls, cmd: RawCommand) -> ContinueDialogueCommand:
        return ContinueDialogueCommand(text=cast(str, cmd.parameters[0]))

    @override
    def to_raw_command(self) -> RawCommand:
        return RawCommand(
            code=401,
            parameters=[self.text],
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
        return CommentCommand(comment=cast(str, cmd.parameters[0]))

    @override
    def to_raw_command(self) -> RawCommand:
        return RawCommand(
            code=108,
            parameters=[self.comment],
        )

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {
            "command": "CommentCommand",
            "comment": self.comment,
        }


@attrs.define(kw_only=True)
class ContinuedCommentCommand(CommentCommand):
    """
    An event command that continues a comment.
    """

    @classmethod
    @override
    def from_raw_command(cls, cmd: RawCommand) -> ContinuedCommentCommand:
        return ContinuedCommentCommand(comment=cast(str, cmd.parameters[0]))

    @override
    def to_raw_command(self) -> RawCommand:
        return RawCommand(
            code=408,
            parameters=[self.comment],
        )

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {
            "command": "ContinuedCommentCommand",
            "comment": self.comment,
        }


class ChoiceCancelledAction(enum.IntEnum):
    Disallow = 0
    Choice1 = 1
    Choice2 = 2
    Choice3 = 3
    Choice4 = 4
    Branch = 5


@attrs.define(kw_only=True)
class SelectChoiceCommand(RubyBaseEventCommand):
    """
    An event command that shows a choice to the player.
    """

    # Who fucking knows what the default index is for.
    # It's either been zero, len(choices), len(choices) + 1.

    choices: list[str] = attrs.field()
    when_cancelled: ChoiceCancelledAction = attrs.field()

    @classmethod
    @override
    def from_raw_command(cls, cmd: RawCommand) -> SelectChoiceCommand:
        return SelectChoiceCommand(
            choices=cast(list[str], cmd.parameters[0]),
            when_cancelled=ChoiceCancelledAction(cmd.parameters[1]),
        )

    @override
    def to_raw_command(self) -> RawCommand:
        return RawCommand(
            code=102,
            parameters=[self.choices, self.when_cancelled.value],
        )

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {
            "command": "SelectChoiceCommand",
            "choices": self.choices,
            "when_cancelled": self.when_cancelled.name,
        }
