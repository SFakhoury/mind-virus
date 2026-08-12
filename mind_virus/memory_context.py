from __future__ import annotations

from dataclasses import dataclass

from mind_virus.agent import Agent
from mind_virus.memory import Memory


@dataclass(frozen=True)
class ConversationContext:
    """Grounded information available before a resident speaks."""

    partner_name: str
    location_name: str
    activity: str
    topic: str = ""

    def __post_init__(self) -> None:
        if not self.partner_name.strip():
            raise ValueError("Conversation partner cannot be empty.")
        if not self.location_name.strip():
            raise ValueError("Conversation location cannot be empty.")
        if not self.activity.strip():
            raise ValueError("Conversation activity cannot be empty.")

    @property
    def retrieval_query(self) -> str:
        parts = [
            self.partner_name.strip(),
            self.location_name.strip(),
            self.activity.strip(),
            self.topic.strip(),
        ]
        return " ".join(part for part in parts if part)


@dataclass(frozen=True)
class RetrievedConversationContext:
    query: str
    memories: tuple[Memory, ...]


def retrieve_conversation_context(
    agent: Agent,
    context: ConversationContext,
    *,
    limit: int = 5,
) -> RetrievedConversationContext:
    """Retrieve memories grounded in the current conversational situation."""
    memories = agent.recall(context.retrieval_query, limit=limit)
    return RetrievedConversationContext(
        query=context.retrieval_query,
        memories=tuple(memories),
    )
