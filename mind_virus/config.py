from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path


@dataclass(frozen=True)
class ExperimentConfig:
    """Reproducible limits and settings for a model-backed experiment."""

    name: str = "phase4-dry-run"
    model: str = "gpt-5.6-luna"
    seed: int = 2026
    trials_per_condition: int = 5
    conditions: tuple[str, ...] = ("baseline", "skeptical")
    agents_per_trial: int = 4
    skeptic_fraction: float = 0.35
    maximum_api_calls: int = 30
    maximum_cost_usd: float = 0.25
    estimated_input_tokens_per_call: int = 500
    estimated_output_tokens_per_call: int = 80
    dry_run: bool = True

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Experiment name cannot be empty.")

        if not self.model.strip():
            raise ValueError("Model cannot be empty.")

        if self.trials_per_condition < 1:
            raise ValueError(
                "Trials per condition must be at least 1."
            )

        if self.agents_per_trial < 2:
            raise ValueError(
                "Agents per trial must be at least 2."
            )

        if not self.conditions:
            raise ValueError(
                "At least one condition is required."
            )

        if len(set(self.conditions)) != len(self.conditions):
            raise ValueError(
                "Experiment conditions must be unique."
            )

        if not 0.0 <= self.skeptic_fraction <= 1.0:
            raise ValueError(
                "Skeptic fraction must be between 0 and 1."
            )

        if self.maximum_api_calls < 0:
            raise ValueError(
                "Maximum API calls cannot be negative."
            )

        if self.maximum_cost_usd < 0:
            raise ValueError(
                "Maximum cost cannot be negative."
            )

    @property
    def planned_api_calls(self) -> int:
        """One interpretation per transmission between agents."""
        calls_per_trial = self.agents_per_trial - 1

        return (
            len(self.conditions)
            * self.trials_per_condition
            * calls_per_trial
        )

    @property
    def estimated_cost_usd(self) -> float:
        """Estimate standard GPT-5.6 Luna token cost."""
        input_cost = (
            self.planned_api_calls
            * self.estimated_input_tokens_per_call
            / 1_000_000
            * 1.00
        )
        output_cost = (
            self.planned_api_calls
            * self.estimated_output_tokens_per_call
            / 1_000_000
            * 6.00
        )

        return input_cost + output_cost

    def validate_budget(self) -> None:
        """Reject a plan that exceeds either safety limit."""
        if self.planned_api_calls > self.maximum_api_calls:
            raise ValueError(
                "Planned API calls exceed the configured limit."
            )

        if self.estimated_cost_usd > self.maximum_cost_usd:
            raise ValueError(
                "Estimated cost exceeds the configured limit."
            )

    def save(self, path: str | Path) -> Path:
        """Save the exact configuration used by an experiment."""
        output = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)

        data = asdict(self)
        data["conditions"] = list(self.conditions)
        data["planned_api_calls"] = self.planned_api_calls
        data["estimated_cost_usd"] = self.estimated_cost_usd

        output.write_text(
            json.dumps(data, indent=2),
            encoding="utf-8",
        )

        return output
