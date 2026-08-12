from __future__ import annotations

from dataclasses import dataclass
import re

from mind_virus.conversation_planning import GroundedConversationPlan


_FUNCTION_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "but", "by", "for",
    "from", "have", "here", "i", "in", "is", "it", "my", "of", "on",
    "or", "so", "that", "the", "there", "this", "to", "we", "with",
}


@dataclass(frozen=True)
class GroundingValidation:
    accepted: bool
    reasons: tuple[str, ...]
    unsupported_terms: tuple[str, ...]


def validate_grounded_dialogue(
    message: str,
    plan: GroundedConversationPlan,
    *,
    minimum_coverage: float = 0.6,
) -> GroundingValidation:
    """Reject factual-looking model text unsupported by supplied context."""
    if not message.strip():
        return GroundingValidation(False, ("message is empty",), ())
    if not 0.0 <= minimum_coverage <= 1.0:
        raise ValueError("Minimum grounding coverage must be between 0 and 1.")

    evidence = " ".join(
        (*plan.grounding, plan.location_name, plan.topic)
    ).casefold()
    evidence_terms = _terms(evidence)
    message_terms = _terms(message)
    meaningful = message_terms - _FUNCTION_WORDS
    unsupported = sorted(meaningful - evidence_terms)
    covered = meaningful & evidence_terms
    coverage = len(covered) / len(meaningful) if meaningful else 1.0
    reasons: list[str] = []
    if not plan.grounding and _asserts_fact(message):
        reasons.append("factual statement has no retrieved memory support")
    if coverage < minimum_coverage:
        reasons.append(f"grounding coverage {coverage:.2f} is below {minimum_coverage:.2f}")
    evidence_numbers = set(re.findall(r"\b\d+(?:\.\d+)?\b", evidence))
    message_numbers = set(re.findall(r"\b\d+(?:\.\d+)?\b", message))
    if message_numbers - evidence_numbers:
        reasons.append("message introduces unsupported numbers")
    evidence_names = set(re.findall(r"\b[A-Z][a-z]+\b", " ".join(plan.grounding)))
    allowed_names = evidence_names | set(re.findall(r"\b[A-Z][a-z]+\b", plan.location_name))
    message_names = set(re.findall(r"\b[A-Z][a-z]+\b", message))
    if message_names - allowed_names - {"I"}:
        reasons.append("message introduces unsupported named entities")
    return GroundingValidation(
        accepted=not reasons,
        reasons=tuple(reasons),
        unsupported_terms=tuple(unsupported),
    )


def _terms(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.casefold()))


def _asserts_fact(message: str) -> bool:
    lowered = message.casefold()
    uncertainty = (
        "do not know", "don't know", "no relevant", "cannot make",
        "can't make", "unsure", "uncertain",
    )
    return not any(marker in lowered for marker in uncertainty)
