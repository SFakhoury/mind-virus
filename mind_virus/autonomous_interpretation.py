from __future__ import annotations

from dataclasses import dataclass

from mind_virus.agent import Agent


@dataclass(frozen=True)
class ListenerInterpretation:
    remembered_message: str
    believes_message: bool
    repeats_message: bool
    confidence: float
    acceptance_threshold: float
    reason: str
    relevant_memory_ids: tuple[str, ...]


def interpret_autonomous_message(
    listener: Agent,
    speaker: Agent,
    message: str,
    *,
    supporting_memory_ids: tuple[str, ...] = (),
    relationship_trust: float = 0.5,
) -> ListenerInterpretation:
    """Interpret speech separately from belief and repetition decisions."""
    if not message.strip():
        raise ValueError("Autonomous message cannot be empty.")
    if not 0.0 <= relationship_trust <= 1.0:
        raise ValueError("Relationship trust must be between 0 and 1.")

    relevant = listener.recall(message, limit=3)
    contradictory = any(_signals_contradiction(memory.content) for memory in relevant)
    personality = listener.personality.casefold()
    skeptical = any(
        term in personality
        for term in ("skeptical", "careful", "cautious", "evidence")
    )
    threshold = 0.7 if skeptical else 0.5
    confidence = 0.25 + 0.2 * relationship_trust
    if supporting_memory_ids:
        confidence += 0.25
    if any(memory.source == "observation" for memory in relevant):
        confidence += 0.10
    if contradictory:
        confidence -= 0.40
    confidence = min(1.0, max(0.0, confidence))
    believes = confidence >= threshold
    repeats = (
        not contradictory
        and bool(supporting_memory_ids)
        and confidence >= (0.65 if skeptical else 0.5)
    )
    if contradictory:
        reason = "relevant private memory contradicts the message"
    elif believes:
        reason = "memory support and relationship trust meet the belief threshold"
    elif supporting_memory_ids:
        reason = "the message is grounded, but confidence remains below the threshold"
    else:
        reason = "the message has no cited private-memory support"

    return ListenerInterpretation(
        remembered_message=f'{speaker.name} shared: "{message.strip()}"',
        believes_message=believes,
        repeats_message=repeats,
        confidence=confidence,
        acceptance_threshold=threshold,
        reason=reason,
        relevant_memory_ids=tuple(memory.id for memory in relevant),
    )


def _signals_contradiction(content: str) -> bool:
    lowered = content.casefold()
    padded = f" {lowered} "
    return any(
        marker in padded
        for marker in (
            " no ", " not ", " never", " incorrect", " unsupported",
            "false", "contradict",
        )
    )
