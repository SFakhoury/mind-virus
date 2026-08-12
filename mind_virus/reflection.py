from __future__ import annotations

from collections import Counter
import re

from mind_virus.agent import Agent
from mind_virus.memory import Memory


_STOP_WORDS = {
    "about", "after", "again", "also", "been", "before", "being",
    "from", "have", "into", "that", "their", "there", "these", "they",
    "this", "was", "were", "what", "when", "where", "which", "while",
    "with", "would", "said", "something",
}


def reflect_on_memories(
    agent: Agent,
    topic: str,
    *,
    minimum_memories: int = 3,
    limit: int = 5,
) -> Memory | None:
    """Create one traceable higher-level memory from related experiences."""
    if not topic.strip():
        raise ValueError("Reflection topic cannot be empty.")
    if minimum_memories < 2:
        raise ValueError("Reflection requires at least two source memories.")
    if limit < minimum_memories:
        raise ValueError("Reflection limit cannot be below the minimum.")

    ranked = agent.recall(topic, limit=len(agent.memories) or 1)
    sources = [memory for memory in ranked if memory.source != "reflection"][:limit]
    if len(sources) < minimum_memories:
        return None

    source_ids = tuple(memory.id for memory in sources)
    source_id_set = set(source_ids)
    for memory in agent.memories.all():
        if (
            memory.source == "reflection"
            and set(memory.related_memory_ids) == source_id_set
        ):
            return memory

    recurring = _recurring_terms(sources)
    if recurring:
        insight = ", ".join(recurring[:3])
        content = (
            f"Reflection about {topic.strip()}: across {len(sources)} memories, "
            f"recurring details involve {insight}."
        )
    else:
        content = (
            f"Reflection about {topic.strip()}: {len(sources)} related memories "
            "exist, but they do not yet support a specific recurring conclusion."
        )
    importance = min(
        10,
        max(1, round(sum(memory.importance for memory in sources) / len(sources)) + 1),
    )
    return agent.remember(
        content,
        importance,
        "reflection",
        related_memory_ids=source_ids,
    )


def _recurring_terms(memories: list[Memory]) -> list[str]:
    frequency: Counter[str] = Counter()
    for memory in memories:
        words = {
            word for word in re.findall(r"[a-z0-9]+", memory.content.lower())
            if len(word) > 3 and word not in _STOP_WORDS
        }
        frequency.update(words)
    return [
        word for word, count in sorted(
            frequency.items(),
            key=lambda item: (-item[1], item[0]),
        )
        if count >= 2
    ]
