from dataclasses import dataclass, field
from uuid import uuid4


@dataclass(frozen=True)
class Claim:
    """A traceable version of information transmitted between agents."""

    content: str
    source_agent: str
    confidence: float
    generation: int = 0

    id: str = field(default_factory=lambda: str(uuid4()))
    topic_id: str = field(default_factory=lambda: str(uuid4()))
    parent_id: str | None = None

    def __post_init__(self) -> None:
        cleaned_content = self.content.strip()
        cleaned_source = self.source_agent.strip()

        if not cleaned_content:
            raise ValueError("Claim content cannot be empty.")

        if not cleaned_source:
            raise ValueError("Claim source agent cannot be empty.")

        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                "Claim confidence must be between 0 and 1."
            )

        if self.generation < 0:
            raise ValueError(
                "Claim generation cannot be negative."
            )

        if not self.id.strip():
            raise ValueError("Claim ID cannot be empty.")

        if not self.topic_id.strip():
            raise ValueError("Claim topic ID cannot be empty.")

        if self.generation == 0 and self.parent_id is not None:
            raise ValueError(
                "An original claim cannot have a parent."
            )

        if self.generation > 0 and self.parent_id is None:
            raise ValueError(
                "A transmitted claim must have a parent."
            )

        object.__setattr__(self, "content", cleaned_content)
        object.__setattr__(self, "source_agent", cleaned_source)

    def transmit(
        self,
        content: str,
        source_agent: str,
        confidence: float,
    ) -> "Claim":
        """Create the next traceable generation of this claim."""
        return Claim(
            content=content,
            source_agent=source_agent,
            confidence=confidence,
            generation=self.generation + 1,
            topic_id=self.topic_id,
            parent_id=self.id,
        )
