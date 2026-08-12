from __future__ import annotations

import os
from typing import Any

from pydantic import BaseModel, Field

from .agent import Agent
from .decision import ModelUsage


class TownDialogue(BaseModel):
    """One role-aware exchange generated for two town residents."""

    speaker_message: str = Field(min_length=1, max_length=240)
    listener_reply: str = Field(min_length=1, max_length=240)
    topic: str = Field(min_length=1, max_length=80)
    references_rumor: bool


class OpenAITownDialogueMaker:
    """Generate an exchange using roles and private memories."""

    def __init__(self, model: str | None = None, client: Any | None = None):
        if client is None:
            from openai import OpenAI

            client = OpenAI()
        self._client = client
        self.model = model or os.getenv("MIND_VIRUS_MODEL") or "gpt-5.6-luna"
        self.usage = ModelUsage()

    def __call__(self, speaker: Agent, listener: Agent) -> TownDialogue:
        speaker_memories = speaker.recall("recent town events and rumors", limit=3)
        listener_memories = listener.recall("recent town events and rumors", limit=3)
        speaker_context = "\n".join(f"- {m.content}" for m in speaker_memories)
        listener_context = "\n".join(f"- {m.content}" for m in listener_memories)

        response = self._client.responses.parse(
            model=self.model,
            instructions=(
                "Write one short, natural exchange between two fictional town residents. "
                "Respect their roles, personalities, and private memories. They may discuss "
                "the bakery rumor, its correction, or the fact that evidence is absent. "
                "Use ONLY facts explicitly contained in the supplied memories. Never invent "
                "a document, written statement, inspection, record, announcement, witness, "
                "conversation, observation, plan, or town event. A job or role does not imply "
                "access to unstated evidence. If the memories contain no direct evidence, say "
                "that there is no direct evidence. Never make a resident assert something "
                "contradicted by firsthand memory. Do not force rumor propagation. Each "
                "message must be at most two sentences."
            ),
            input=(
                f"Speaker: {speaker.name}\n"
                f"Speaker personality and role: {speaker.personality}\n"
                f"Speaker memories:\n{speaker_context or '- None'}\n\n"
                f"Listener: {listener.name}\n"
                f"Listener personality and role: {listener.personality}\n"
                f"Listener memories:\n{listener_context or '- None'}"
            ),
            text_format=TownDialogue,
            reasoning={"effort": "none"},
        )
        self.usage.calls += 1
        if response.usage is not None:
            self.usage.input_tokens += int(response.usage.input_tokens)
            self.usage.output_tokens += int(response.usage.output_tokens)
        dialogue = response.output_parsed
        if dialogue is None:
            raise ValueError("The model returned no town dialogue.")
        return dialogue
