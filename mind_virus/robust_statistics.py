from __future__ import annotations

from dataclasses import dataclass
import math
from statistics import mean, stdev

from mind_virus.statistics import paired_bootstrap


@dataclass(frozen=True)
class PairedEffectSize:
    sample_size: int
    mean_difference: float
    standardized_effect_dz: float | None
    confidence_interval_low: float
    confidence_interval_high: float


@dataclass(frozen=True)
class MultipleComparisonResult:
    outcome: str
    raw_p_value: float
    adjusted_p_value: float
    rejected: bool


def analyze_paired_effect(
    baseline: list[float],
    intervention: list[float],
    *,
    bootstrap_iterations: int = 10_000,
    seed: int = 2026,
) -> PairedEffectSize:
    """Return raw paired effect, Cohen's dz, and bootstrap uncertainty."""
    estimate = paired_bootstrap(
        baseline, intervention, iterations=bootstrap_iterations, seed=seed
    )
    differences = [
        treated - control for control, treated in zip(baseline, intervention)
    ]
    if len(differences) < 2:
        standardized = None
    else:
        spread = stdev(differences)
        standardized = mean(differences) / spread if spread > 0 else None
    return PairedEffectSize(
        sample_size=len(differences),
        mean_difference=estimate.mean_difference,
        standardized_effect_dz=standardized,
        confidence_interval_low=estimate.confidence_interval_low,
        confidence_interval_high=estimate.confidence_interval_high,
    )


def adjust_benjamini_hochberg(
    p_values: dict[str, float],
    *,
    alpha: float = 0.05,
) -> tuple[MultipleComparisonResult, ...]:
    """Control false-discovery rate across a named family of outcomes."""
    if not p_values:
        raise ValueError("At least one p-value is required.")
    if not 0.0 < alpha < 1.0:
        raise ValueError("Alpha must be between 0 and 1.")
    if any(
        not isinstance(value, (int, float))
        or not math.isfinite(value)
        or not 0.0 <= value <= 1.0
        for value in p_values.values()
    ):
        raise ValueError("P-values must be finite numbers between 0 and 1.")
    ordered = sorted(p_values.items(), key=lambda item: (item[1], item[0]))
    count = len(ordered)
    adjusted: list[float] = [0.0] * count
    running_minimum = 1.0
    for index in range(count - 1, -1, -1):
        rank = index + 1
        candidate = ordered[index][1] * count / rank
        running_minimum = min(running_minimum, candidate)
        adjusted[index] = min(1.0, running_minimum)
    by_name = {
        name: MultipleComparisonResult(name, raw, corrected, corrected <= alpha)
        for (name, raw), corrected in zip(ordered, adjusted)
    }
    return tuple(by_name[name] for name in p_values)
