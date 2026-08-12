from __future__ import annotations

from dataclasses import dataclass
import random
from statistics import mean


@dataclass(frozen=True)
class PairedEstimate:
    """A paired skeptical-minus-baseline effect estimate."""

    sample_size: int
    baseline_mean: float
    skeptical_mean: float
    mean_difference: float
    confidence_interval_low: float
    confidence_interval_high: float


def paired_bootstrap(
    baseline: list[float],
    skeptical: list[float],
    *,
    iterations: int = 10_000,
    seed: int = 2026,
) -> PairedEstimate:
    """Estimate a paired mean difference and bootstrap interval."""
    if len(baseline) != len(skeptical):
        raise ValueError(
            "Paired samples must have equal lengths."
        )

    if not baseline:
        raise ValueError(
            "Paired samples cannot be empty."
        )

    if iterations < 100:
        raise ValueError(
            "Bootstrap iterations must be at least 100."
        )

    differences = [
        skeptical_value - baseline_value
        for baseline_value, skeptical_value
        in zip(baseline, skeptical)
    ]

    rng = random.Random(seed)
    bootstrap_means: list[float] = []

    for _ in range(iterations):
        resampled = [
            rng.choice(differences)
            for _ in differences
        ]
        bootstrap_means.append(mean(resampled))

    bootstrap_means.sort()

    lower_index = int(iterations * 0.025)
    upper_index = min(
        iterations - 1,
        int(iterations * 0.975),
    )

    return PairedEstimate(
        sample_size=len(differences),
        baseline_mean=mean(baseline),
        skeptical_mean=mean(skeptical),
        mean_difference=mean(differences),
        confidence_interval_low=(
            bootstrap_means[lower_index]
        ),
        confidence_interval_high=(
            bootstrap_means[upper_index]
        ),
    )
