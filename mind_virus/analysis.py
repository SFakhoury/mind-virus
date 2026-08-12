from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
from statistics import mean


UNCERTAINTY_WORDS = {
    "alleged",
    "apparently",
    "claim",
    "claimed",
    "claims",
    "heard",
    "might",
    "maybe",
    "perhaps",
    "reportedly",
    "rumor",
    "rumour",
    "uncertain",
    "unconfirmed",
}


@dataclass(frozen=True)
class ChainMetrics:
    generations: int
    original_similarity: float
    average_step_similarity: float
    uncertainty_mentions: int


def word_set(text: str) -> set[str]:
    """Normalize text into lowercase words."""
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def similarity(first: str, second: str) -> float:
    """Calculate Jaccard similarity between two messages."""
    first_words = word_set(first)
    second_words = word_set(second)

    if not first_words and not second_words:
        return 1.0

    if not first_words or not second_words:
        return 0.0

    return len(first_words & second_words) / len(
        first_words | second_words
    )


def analyze_chain(
    transcript: list[dict[str, object]],
) -> ChainMetrics:
    """Measure mutation and uncertainty across a propagation chain."""
    if len(transcript) < 2:
        raise ValueError(
            "A propagation chain needs at least two generations."
        )

    messages: list[str] = []

    for entry in transcript:
        message = entry.get("message")

        if not isinstance(message, str) or not message.strip():
            raise ValueError(
                "Every transcript entry needs a non-empty message."
            )

        messages.append(message)

    step_similarities = [
        similarity(messages[index - 1], messages[index])
        for index in range(1, len(messages))
    ]

    uncertainty_mentions = sum(
        len(word_set(message) & UNCERTAINTY_WORDS)
        for message in messages
    )

    return ChainMetrics(
        generations=len(messages) - 1,
        original_similarity=similarity(
            messages[0],
            messages[-1],
        ),
        average_step_similarity=mean(step_similarities),
        uncertainty_mentions=uncertainty_mentions,
    )


def load_and_analyze(path: str | Path) -> ChainMetrics:
    """Load a saved JSON transcript and analyze it."""
    transcript_path = Path(path)

    with transcript_path.open(encoding="utf-8") as input_file:
        transcript = json.load(input_file)

    if not isinstance(transcript, list):
        raise ValueError("Transcript must contain a JSON list.")

    return analyze_chain(transcript)
