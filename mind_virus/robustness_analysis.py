from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from statistics import mean, median
from typing import Literal


Direction = Literal["lower", "higher"]


@dataclass(frozen=True)
class RobustnessObservation:
    cell_id: str
    outcome: str
    effect: float
    confidence_interval_low: float
    confidence_interval_high: float

    def __post_init__(self) -> None:
        if self.confidence_interval_low > self.confidence_interval_high:
            raise ValueError("Confidence interval bounds are reversed.")
        if not self.confidence_interval_low <= self.effect <= self.confidence_interval_high:
            raise ValueError("Effect estimate must lie inside its confidence interval.")


@dataclass(frozen=True)
class RobustnessSummary:
    outcome: str
    expected_direction: Direction
    cells: int
    mean_effect: float
    median_effect: float
    minimum_effect: float
    maximum_effect: float
    direction_consistency: float
    significant_supporting_cells: int
    significant_contradicting_cells: int
    inconclusive_cells: int
    required_consistency: float
    conclusion_survives: bool

    def save(self, path: str | Path) -> Path:
        output = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")
        return output


def summarize_robustness(
    observations: list[RobustnessObservation],
    *,
    expected_direction: Direction,
    minimum_consistency: float = 0.8,
) -> RobustnessSummary:
    if not observations:
        raise ValueError("At least one robustness observation is required.")
    outcomes = {item.outcome for item in observations}
    if len(outcomes) != 1:
        raise ValueError("A robustness summary covers exactly one outcome.")
    if len({item.cell_id for item in observations}) != len(observations):
        raise ValueError("Robustness cell IDs must be unique within an outcome.")
    if expected_direction not in {"lower", "higher"}:
        raise ValueError("Expected direction must be lower or higher.")
    if not 0.5 <= minimum_consistency <= 1.0:
        raise ValueError("Minimum consistency must be between 0.5 and 1.")

    supports = lambda value: value < 0 if expected_direction == "lower" else value > 0
    effects = [item.effect for item in observations]
    direction_count = sum(supports(value) for value in effects)
    supporting = 0
    contradicting = 0
    inconclusive = 0
    for item in observations:
        excludes_zero = (
            item.confidence_interval_high < 0
            or item.confidence_interval_low > 0
        )
        if not excludes_zero:
            inconclusive += 1
        elif supports(item.effect):
            supporting += 1
        else:
            contradicting += 1
    consistency = direction_count / len(observations)
    return RobustnessSummary(
        outcome=next(iter(outcomes)),
        expected_direction=expected_direction,
        cells=len(observations),
        mean_effect=mean(effects),
        median_effect=median(effects),
        minimum_effect=min(effects),
        maximum_effect=max(effects),
        direction_consistency=consistency,
        significant_supporting_cells=supporting,
        significant_contradicting_cells=contradicting,
        inconclusive_cells=inconclusive,
        required_consistency=minimum_consistency,
        conclusion_survives=(
            consistency >= minimum_consistency
            and supporting > 0
            and contradicting == 0
        ),
    )
