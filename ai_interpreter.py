from __future__ import annotations

import os
from typing import Any

from agent import Agent


class OpenAIInterpreter:
    """Use an OpenAI model to form listener-specific memories."""

    def __init__(
        self,
        model: str | None = None,
        client: Any | None = None,
    ) -> None:
        if client is None:
            from openai import OpenAI

            client = OpenAI()

        self._client = client
        self.model = (
            model
            or os.getenv("MIND_VIRUS_MODEL")
            or "gpt-5.6-luna"
        )

    def __call__(
        self,
        listener: Agent,
        speaker: Agent,
        message: str,
    ) -> str:
        """Interpret dialogue from the listener's perspective."""
        relevant_memories = listener.recall(
            context=message,
            limit=3,
        )

        memory_context = "\n".join(
            f"- {memory.content}"
            for memory in relevant_memories
        )

        if not memory_context:
            memory_context = "- No relevant prior memories."

        instructions = (
            "You simulate private memory formation for one fictional "
            "agent in a research simulation. Rewrite the spoken message "
            "as the listener would privately remember it. Reflect the "
            "listener's personality and relevant memories. Preserve "
            "uncertainty and attribution. Do not convert hearsay into "
            "established fact. Return only one concise memory sentence."
        )

        prompt = (
            f"Listener: {listener.name}\n"
            f"Listener personality: {listener.personality}\n"
            f"Speaker: {speaker.name}\n"
            f"Spoken message: {message}\n"
            f"Relevant listener memories:\n{memory_context}"
        )

        response = self._client.responses.create(
            model=self.model,
            instructions=instructions,
            input=prompt,
            reasoning={"effort": "none"},
            text={"verbosity": "low"},
        )

        interpretation = response.output_text.strip()

        if not interpretation:
            raise ValueError(
                "The model returned an empty interpretation."
            )

        return interpretation
