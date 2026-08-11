from dataclasses import dataclass

from claim import Claim


@dataclass(frozen=True)
class Belief:
    """A claim an agent currently accepts, with agent-level confidence."""

    topic_id: str
    claim_id: str
    content: str
    confidence: float
    generation: int

    def __post_init__(self) -> None:
        if not self.topic_id.strip():
            raise ValueError("Belief topic ID cannot be empty.")

        if not self.claim_id.strip():
            raise ValueError("Belief claim ID cannot be empty.")

        if not self.content.strip():
            raise ValueError("Belief content cannot be empty.")

        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                "Belief confidence must be between 0 and 1."
            )

        if self.generation < 0:
            raise ValueError(
                "Belief generation cannot be negative."
            )

    @classmethod
    def from_claim(
        cls,
        claim: Claim,
        confidence: float | None = None,
    ) -> "Belief":
        """Create a belief from an accepted claim."""
        belief_confidence = (
            claim.confidence
            if confidence is None
            else confidence
        )

        return cls(
            topic_id=claim.topic_id,
            claim_id=claim.id,
            content=claim.content,
            confidence=belief_confidence,
            generation=claim.generation,
        )
