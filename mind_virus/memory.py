from dataclasses import dataclass, field
from datetime import datetime, timezone
import math
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
    related_memory_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.content.strip():
            raise ValueError("Memory content cannot be empty.")

        if not 1 <= self.importance <= 10:
            raise ValueError(
                "Memory importance must be between 1 and 10."
            )

        if self.id in self.related_memory_ids:
            raise ValueError("A memory cannot reference itself.")


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

    def retrieve(
        self,
        query: str,
        limit: int = 5,
    ) -> list[Memory]:
        """Rank memories by recency, importance, and relevance."""
        if not query.strip():
            raise ValueError("Retrieval query cannot be empty.")

        if limit < 1:
            raise ValueError("Limit must be at least 1.")

        now = datetime.now(timezone.utc)

        scored = [
            (
                self._score(memory, query, now),
                memory.created_at,
                memory,
            )
            for memory in self._memories
        ]

        scored.sort(
            key=lambda item: (item[0], item[1]),
            reverse=True,
        )

        return [
            memory
            for _, _, memory in scored[:limit]
        ]

    @staticmethod
    def _score(
        memory: Memory,
        query: str,
        now: datetime,
    ) -> float:
        """Calculate the combined Phase 1 retrieval score."""
        age_hours = max(
            0.0,
            (now - memory.created_at).total_seconds() / 3600,
        )

        recency = math.exp(-age_hours / 24.0)
        importance = memory.importance / 10.0
        relevance = MemoryStream._lexical_relevance(
            query,
            memory.content,
        )

        return recency + importance + relevance

    @staticmethod
    def _lexical_relevance(
        query: str,
        content: str,
    ) -> float:
        """Calculate temporary Phase 1 word-overlap relevance."""
        query_words = set(
            re.findall(r"[a-z0-9]+", query.lower())
        )
        content_words = set(
            re.findall(r"[a-z0-9]+", content.lower())
        )

        if not query_words or not content_words:
            return 0.0

        intersection = query_words & content_words
        union = query_words | content_words

        return len(intersection) / len(union)

    def __len__(self) -> int:
        """Return the number of stored memories."""
        return len(self._memories)

