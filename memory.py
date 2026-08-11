from dataclasses import dataclass, field
from datetime import datetime, timezone
import re
from typing import Literal
from uuid import uuid4


MemorySource = Literal["observation", "dialogue", "reflection"]


@dataclass
class Memory:
    """A single experience stored in an agent's private memory stream."""

    content: str
    importance: int
    source: MemorySource

    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def __post_init__(self) -> None:
        if not self.content.strip():
            raise ValueError("Memory content cannot be empty.")

        if not 1 <= self.importance <= 10:
            raise ValueError("Memory importance must be between 1 and 10.")


class MemoryStream:
    """Chronological collection of memories belonging to one agent."""

    def __init__(self) -> None:
        self._memories: list[Memory] = []

    def add(self, memory: Memory) -> None:
        """Store a memory in the stream."""
        self._memories.append(memory)

    def all(self) -> list[Memory]:
        """Return all memories in chronological order."""
        return list(self._memories)

    def recent(self, limit: int = 5) -> list[Memory]:
        """Return the most recent memories, newest first."""
        if limit < 1:
            raise ValueError("Limit must be at least 1.")

        return list(reversed(self._memories[-limit:]))

    def retrieve(self, query: str, limit: int = 5) -> list[Memory]:
        """Return memories matching a query, ranked deterministically.

        Memories with more query-word matches rank first. Importance breaks
        relevance ties, followed by recency. Memories with no matching words
        are excluded.
        """
        if not query.strip():
            raise ValueError("Query cannot be empty.")

        if limit < 1:
            raise ValueError("Limit must be at least 1.")

        query_words = self._words(query)
        ranked: list[tuple[int, int, int, Memory]] = []

        for position, memory in enumerate(self._memories):
            relevance = len(query_words & self._words(memory.content))
            if relevance:
                ranked.append(
                    (relevance, memory.importance, position, memory)
                )

        ranked.sort(key=lambda item: item[:3], reverse=True)
        return [item[3] for item in ranked[:limit]]

    @staticmethod
    def _words(text: str) -> set[str]:
        """Normalize text into lowercase words for basic retrieval."""
        return set(re.findall(r"[a-z0-9]+", text.lower()))

    def __len__(self) -> int:
        """Return the number of memories in the stream."""
        return len(self._memories)
