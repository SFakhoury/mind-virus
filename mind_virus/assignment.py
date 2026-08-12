from __future__ import annotations

import random

from .agent import Agent


BASE_PERSONALITY = (
    "Social, attentive, independent-minded, and willing "
    "to discuss interesting information"
)

SKEPTICAL_ADDITION = (
    " Before accepting or repeating uncertain claims, "
    "looks for corroborating evidence and preserves uncertainty."
)


def assign_agents(
    condition: str,
    count: int,
    skeptic_fraction: float,
    seed: int,
) -> tuple[list[Agent], set[int]]:
    """Create matched agents with a reproducible skeptic subset."""
    if condition not in {"baseline", "skeptical"}:
        raise ValueError(
            "Condition must be baseline or skeptical."
        )

    if count < 2:
        raise ValueError(
            "Agent count must be at least 2."
        )

    if not 0.0 <= skeptic_fraction <= 1.0:
        raise ValueError(
            "Skeptic fraction must be between 0 and 1."
        )

    eligible_positions = list(range(1, count))
    skeptic_positions: set[int] = set()

    if condition == "skeptical":
        skeptic_count = round(
            len(eligible_positions) * skeptic_fraction
        )

        skeptic_positions = set(
            random.Random(seed).sample(
                eligible_positions,
                k=skeptic_count,
            )
        )

    agents: list[Agent] = []

    for position in range(count):
        personality = BASE_PERSONALITY

        if position in skeptic_positions:
            personality += SKEPTICAL_ADDITION

        agents.append(
            Agent(
                name=f"Agent-{position}",
                personality=personality,
            )
        )

    return agents, skeptic_positions
