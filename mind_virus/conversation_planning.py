from __future__ import annotations

from dataclasses import dataclass

from mind_virus.agent import Agent
from mind_virus.memory_context import (
    ConversationContext,
    retrieve_conversation_context,
)


@dataclass(frozen=True)
class GroundedConversationPlan:
    """An auditable proposal for what one resident can discuss."""

    speaker_name: str
    listener_name: str
    location_name: str
    topic: str
    retrieval_query: str
    memory_ids: tuple[str, ...]
    grounding: tuple[str, ...]
    proposed_message: str

    @property
    def has_memory_support(self) -> bool:
        return bool(self.memory_ids)


def plan_grounded_conversation(
    speaker: Agent,
    listener: Agent,
    context: ConversationContext,
    *,
    memory_limit: int = 3,
) -> GroundedConversationPlan:
    """Plan a message using only memories retrieved for the current context."""
    if context.partner_name.casefold() != listener.name.casefold():
        raise ValueError("Conversation context partner must match the listener.")

    retrieved = retrieve_conversation_context(
        speaker,
        context,
        limit=memory_limit,
    )
    grounding = tuple(memory.content for memory in retrieved.memories)
    topic = context.topic.strip() or context.activity.strip()
    if grounding:
        proposed_message = f"I remember: {grounding[0]}"
    else:
        proposed_message = (
            f"I do not have a relevant memory about {topic}, "
            "so I cannot make a factual claim about it."
        )

    return GroundedConversationPlan(
        speaker_name=speaker.name,
        listener_name=listener.name,
        location_name=context.location_name,
        topic=topic,
        retrieval_query=retrieved.query,
        memory_ids=tuple(memory.id for memory in retrieved.memories),
        grounding=grounding,
        proposed_message=proposed_message,
    )
