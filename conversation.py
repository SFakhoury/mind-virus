from collections.abc import Callable

from agent import Agent
from memory import Memory


Interpreter = Callable[[Agent, Agent, str], str]


class Conversation:
    """Deliver dialogue and let each listener interpret it privately."""

    def __init__(self, interpreter: Interpreter) -> None:
        if not callable(interpreter):
            raise TypeError("Interpreter must be callable.")

        self._interpreter = interpreter

    def deliver(
        self,
        speaker: Agent,
        listener: Agent,
        message: str,
        importance: int,
    ) -> Memory:
        """Deliver one statement from a speaker to a listener."""
        cleaned_message = message.strip()

        if not cleaned_message:
            raise ValueError("Conversation message cannot be empty.")

        interpretation = self._interpreter(
            listener,
            speaker,
            cleaned_message,
        )

        if not isinstance(interpretation, str):
            raise TypeError(
                "Interpreter must return a string."
            )

        return listener.hear(
            speaker=speaker,
            message=cleaned_message,
            importance=importance,
            interpretation=interpretation,
        )
