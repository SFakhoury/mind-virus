from __future__ import annotations

from dataclasses import dataclass
import re

from mind_virus.agent import Agent
from mind_virus.memory import Memory


@dataclass(frozen=True)
class ConversationTopic:
    label: str
    source_memory_ids: tuple[str, ...]
    reason: str

    @property
    def memory_grounded(self) -> bool:
        return bool(self.source_memory_ids)


def select_conversation_topic(
    speaker: Agent,
    *,
    partner_name: str,
    location_name: str,
    activity: str,
) -> ConversationTopic:
    """Select a topic from memories relevant to the shared situation."""
    parts = (partner_name.strip(), location_name.strip(), activity.strip())
    if not all(parts):
        raise ValueError("Topic selection requires partner, location, and activity.")
    query = " ".join(parts)
    candidates = [
        memory for memory in speaker.recall(query, limit=len(speaker.memories) or 1)
        if _has_overlap(query, memory)
    ]
    if candidates:
        memory = candidates[0]
        return ConversationTopic(
            label=" ".join(memory.content.split())[:80],
            source_memory_ids=(memory.id,),
            reason=(
                f"selected a private memory relevant to {partner_name} "
                f"at {location_name}"
            ),
        )
    return ConversationTopic(
        label=f"{activity} at {location_name}",
        source_memory_ids=(),
        reason="no relevant private memory; using the shared situation",
    )


def _has_overlap(query: str, memory: Memory) -> bool:
    query_words = set(re.findall(r"[a-z0-9]+", query.lower()))
    memory_words = set(re.findall(r"[a-z0-9]+", memory.content.lower()))
    return bool(query_words & memory_words)
