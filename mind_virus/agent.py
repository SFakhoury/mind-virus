from dataclasses import dataclass, field

from .belief import Belief
from .claim import Claim
from .memory import Memory, MemorySource, MemoryStream


@dataclass
class Agent:
    """An agent with a personality, private memories, and beliefs."""

    name: str
    personality: str
    memories: MemoryStream = field(
        default_factory=MemoryStream,
        init=False,
        repr=False,
    )
    _beliefs: dict[str, Belief] = field(
        default_factory=dict,
        init=False,
        repr=False,
    )

    def __post_init__(self) -> None:
        self.name = self.name.strip()
        self.personality = self.personality.strip()

        if not self.name:
            raise ValueError("Agent name cannot be empty.")

        if not self.personality:
            raise ValueError("Agent personality cannot be empty.")

    def remember(
        self,
        content: str,
        importance: int,
        source: MemorySource,
        related_memory_ids: tuple[str, ...] = (),
    ) -> Memory:
        """Create and store a new private memory."""
        memory = Memory(
            content=content,
            importance=importance,
            source=source,
            related_memory_ids=related_memory_ids,
        )
        self.memories.add(memory)
        return memory

    def observe(
        self,
        event: str,
        importance: int,
    ) -> Memory:
        """Store something the agent directly observed."""
        return self.remember(
            content=event,
            importance=importance,
            source="observation",
        )

    def hear(
        self,
        speaker: "Agent",
        message: str,
        importance: int,
        interpretation: str | None = None,
    ) -> Memory:
        """Store the listener's memory of another agent's statement."""
        cleaned_message = message.strip()

        if not cleaned_message:
            raise ValueError("Dialogue message cannot be empty.")

        if interpretation is None:
            memory_content = (
                f'{speaker.name} said: "{cleaned_message}"'
            )
        else:
            cleaned_interpretation = interpretation.strip()

            if not cleaned_interpretation:
                raise ValueError(
                    "Dialogue interpretation cannot be empty."
                )

            memory_content = (
                f"{speaker.name} said something I interpreted as: "
                f'"{cleaned_interpretation}"'
            )

        return self.remember(
            content=memory_content,
            importance=importance,
            source="dialogue",
        )

    def recall(
        self,
        context: str,
        limit: int = 5,
    ) -> list[Memory]:
        """Retrieve memories useful to the current context."""
        return self.memories.retrieve(
            query=context,
            limit=limit,
        )

    def consider_claim(
        self,
        claim: Claim,
        acceptance_threshold: float = 0.5,
        belief_confidence: float | None = None,
    ) -> Belief | None:
        """Accept or reject a claim independently of hearing it."""
        if not 0.0 <= acceptance_threshold <= 1.0:
            raise ValueError(
                "Acceptance threshold must be between 0 and 1."
            )

        evaluated_confidence = (
            claim.confidence
            if belief_confidence is None
            else belief_confidence
        )

        if not 0.0 <= evaluated_confidence <= 1.0:
            raise ValueError(
                "Belief confidence must be between 0 and 1."
            )

        if evaluated_confidence < acceptance_threshold:
            return None

        belief = Belief.from_claim(
            claim,
            confidence=evaluated_confidence,
        )
        self._beliefs[claim.topic_id] = belief
        return belief

    def believes(self, topic_id: str) -> bool:
        """Return whether this agent accepts a topic as a belief."""
        return topic_id in self._beliefs

    def belief_about(self, topic_id: str) -> Belief | None:
        """Return the agent's current belief for a topic."""
        return self._beliefs.get(topic_id)

    def repeat_claim(
        self,
        topic_id: str,
        content: str,
        confidence: float,
    ) -> Claim:
        """Transmit a new generation based on an existing belief."""
        belief = self.belief_about(topic_id)

        if belief is None:
            raise ValueError(
                "Agent cannot repeat a claim it does not believe."
            )

        return Claim(
            content=content,
            source_agent=self.name,
            confidence=confidence,
            generation=belief.generation + 1,
            topic_id=belief.topic_id,
            parent_id=belief.claim_id,
        )

