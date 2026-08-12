from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Any

from pydantic import BaseModel, Field

from .agent import Agent


class TransmissionDecision(BaseModel):
    """A listener's distinct memory, belief, and repetition decisions."""

    remembered_message: str = Field(min_length=1)
    believes_claim: bool
    repeats_claim: bool
    belief_confidence: float = Field(
        ge=0.0,
        le=1.0,
    )
    reason: str = Field(min_length=1)


@dataclass
class ModelUsage:
    """Accumulated model usage for one decision maker."""

    calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0

    @property
    def estimated_cost_usd(self) -> float:
        """Calculate observed GPT-5.6 Luna token cost."""
        input_cost = (
            self.input_tokens
            / 1_000_000
            * 1.00
        )
        output_cost = (
            self.output_tokens
            / 1_000_000
            * 6.00
        )

        return input_cost + output_cost


class OpenAIDecisionMaker:
    """Create structured listener decisions with an OpenAI model."""

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
        self.usage = ModelUsage()

    def __call__(
        self,
        listener: Agent,
        speaker: Agent,
        message: str,
    ) -> TransmissionDecision:
        """Evaluate one statement from the listener's perspective."""
        memories = listener.recall(
            context=message,
            limit=3,
        )

        memory_context = "\n".join(
            f"- {memory.content}"
            for memory in memories
        )

        if not memory_context:
            memory_context = "- No relevant prior memories."

        instructions = (
            "Simulate one fictional listener in a controlled "
            "misinformation experiment. Keep four processes distinct: "
            "hearing, remembering, believing, and repeating. "
            "The listener may remember a claim without believing or "
            "repeating it. Repeats_claim means the listener would "
            "communicate the claim to another person, even if clearly "
            "labeled as uncertain or unverified. Decide according to "
            "the personality and evidence shown. Preserve the exact "
            "speaker identity. The remembered_message must be written "
            "from the listener's perspective and attribute the "
            "statement to the speaker. Do not invent evidence or events."
        )

        prompt = (
            f"Listener name: {listener.name}\n"
            f"Listener personality: {listener.personality}\n"
            f"Speaker name: {speaker.name}\n"
            f"Spoken message: {message}\n"
            f"Relevant listener memories:\n{memory_context}"
        )

        response = self._client.responses.parse(
            model=self.model,
            instructions=instructions,
            input=prompt,
            text_format=TransmissionDecision,
            reasoning={"effort": "none"},
        )

        self.usage.calls += 1

        response_usage = getattr(
            response,
            "usage",
            None,
        )

        if response_usage is not None:
            self.usage.input_tokens += int(
                getattr(
                    response_usage,
                    "input_tokens",
                    0,
                )
            )
            self.usage.output_tokens += int(
                getattr(
                    response_usage,
                    "output_tokens",
                    0,
                )
            )

        decision = response.output_parsed

        if decision is None:
            raise ValueError(
                "The model returned no structured decision."
            )

        return decision
