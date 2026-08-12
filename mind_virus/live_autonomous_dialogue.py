from __future__ import annotations

import os
from typing import Any

from pydantic import BaseModel, Field

from mind_virus.agent import Agent
from mind_virus.api_budget import BudgetLedger
from mind_virus.conversation_planning import GroundedConversationPlan


class StructuredAutonomousDialogue(BaseModel):
    speaker_message: str = Field(min_length=1, max_length=240)
    communicative_intent: str = Field(min_length=1, max_length=80)


class OpenAIAutonomousDialogueMaker:
    """Generate one grounded autonomous message within a persistent budget."""

    def __init__(
        self,
        budget: BudgetLedger,
        *,
        model: str | None = None,
        client: Any | None = None,
        max_output_tokens: int = 120,
    ) -> None:
        if client is None:
            from openai import OpenAI

            client = OpenAI()
        if max_output_tokens < 1:
            raise ValueError("Maximum output tokens must be positive.")
        self._client = client
        self.budget = budget
        self.model = model or os.getenv("MIND_VIRUS_MODEL") or "gpt-5.6-luna"
        self.max_output_tokens = max_output_tokens

    def __call__(
        self,
        speaker: Agent,
        listener: Agent,
        plan: GroundedConversationPlan,
    ) -> StructuredAutonomousDialogue:
        grounding = "\n".join(
            f"- [{memory_id}] {content}"
            for memory_id, content in zip(plan.memory_ids, plan.grounding)
        ) or "- No relevant private memories were retrieved."
        prompt = (
            f"Speaker: {speaker.name}\n"
            f"Speaker role/personality: {speaker.personality}\n"
            f"Listener: {listener.name}\n"
            f"Listener role/personality: {listener.personality}\n"
            f"Location: {plan.location_name}\n"
            f"Selected topic: {plan.topic}\n"
            f"Retrieved private memories:\n{grounding}"
        )
        estimated_input = max(1, len(prompt) // 4)
        reservation = self.budget.reserve(
            speaker.name,
            estimated_input_tokens=estimated_input,
            estimated_output_tokens=self.max_output_tokens,
        )
        try:
            response = self._client.responses.parse(
                model=self.model,
                instructions=(
                    "Generate one short statement by the fictional speaker to the "
                    "listener. Use only facts in the retrieved private memories and "
                    "the explicit location/topic. Never invent evidence, events, "
                    "documents, witnesses, or prior conversations. If no memory "
                    "supports a factual statement, openly say the speaker lacks "
                    "relevant knowledge. Do not decide what the listener believes."
                ),
                input=prompt,
                text_format=StructuredAutonomousDialogue,
                max_output_tokens=self.max_output_tokens,
                reasoning={"effort": "none"},
            )
            usage = getattr(response, "usage", None)
            self.budget.reconcile(
                reservation.id,
                actual_input_tokens=int(getattr(usage, "input_tokens", 0)),
                actual_output_tokens=int(getattr(usage, "output_tokens", 0)),
            )
            dialogue = response.output_parsed
            if dialogue is None:
                raise ValueError("The model returned no structured autonomous dialogue.")
            return dialogue
        except Exception:
            if reservation.id in self.budget.reservations:
                self.budget.cancel(reservation.id)
            raise
