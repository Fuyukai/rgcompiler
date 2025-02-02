from __future__ import annotations

from typing import Any, cast, override

import attrs
from cattr import Converter

from rgss.rpg.commands.base import RawEventCommand, RubyBaseEventCommand

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
    def from_raw_event_command(cls, cmd: RawEventCommand) -> ShowDialogueCommand:
        return ShowDialogueCommand(text=cast(str, cmd.parameters[0]))

    @override
    def get_raw_event_command(self) -> RawEventCommand:
        return RawEventCommand(
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
    def from_raw_event_command(cls, cmd: RawEventCommand) -> ContinueDialogueCommand:
        return ContinueDialogueCommand(text=cast(str, cmd.parameters[0]))

    @override
    def get_raw_event_command(self) -> RawEventCommand:
        return RawEventCommand(
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
    def from_raw_event_command(cls, cmd: RawEventCommand) -> CommentCommand:
        return CommentCommand(comment=cast(str, cmd.parameters[0]))

    @override
    def get_raw_event_command(self) -> RawEventCommand:
        return RawEventCommand(
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
    def from_raw_event_command(cls, cmd: RawEventCommand) -> ContinuedCommentCommand:
        return ContinuedCommentCommand(comment=cast(str, cmd.parameters[0]))

    @override
    def get_raw_event_command(self) -> RawEventCommand:
        return RawEventCommand(
            code=408,
            parameters=[self.comment],
        )

    @override
    def unstructure(self, converter: Converter) -> dict[str, Any]:
        return {
            "command": "ContinuedCommentCommand",
            "comment": self.comment,
        }
