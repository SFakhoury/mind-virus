from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import math
from pathlib import Path
from statistics import NormalDist
from typing import Callable

from mind_virus.agent import Agent
from mind_virus.experiment_spec import ClaimSpec, GeneralizedExperimentSpec, InterventionSpec
from mind_virus.interventions import InterventionAssignment, build_experimental_agents
from mind_virus.preregistration import verify_preregistration
from mind_virus.social_network import SocialNetwork, build_social_network
from mind_virus.trial_design import PlannedTrial, plan_matched_trials


@dataclass(frozen=True)
class TrialContext:
    trial: PlannedTrial
    claim: ClaimSpec
    intervention: InterventionSpec
    network: SocialNetwork
    agents: tuple[Agent, ...]
    assignment: InterventionAssignment


@dataclass(frozen=True)
class ExperimentalResult:
    execution_index: int
    matched_trial_id: str
    claim_id: str
    intervention_type: str
    intervention_intensity: float
    repetition: int
    assignment_seed: int
    network_seed: int
    treated_positions: tuple[int, ...]
    outcomes: dict[str, float]


OutcomeProvider = Callable[[TrialContext], dict[str, float]]


class GeneralizedExperimentRunner:
    def __init__(
        self,
        spec: GeneralizedExperimentSpec,
        outcome_provider: OutcomeProvider,
        *,
        preregistration_path: str | Path | None = None,
    ) -> None:
        self.spec = spec
        self.outcome_provider = outcome_provider
        self.preregistration_path = (
            Path(preregistration_path) if preregistration_path is not None else None
        )
        self._validate_stage()

    def run(self) -> tuple[ExperimentalResult, ...]:
        claims = {claim.id: claim for claim in self.spec.claims}
        interventions = {
            (item.type, item.intensity): item for item in self.spec.interventions
        }
        results: list[ExperimentalResult] = []
        for trial in plan_matched_trials(self.spec).trials:
            intervention = interventions[
                (trial.intervention_type, trial.intervention_intensity)
            ]
            network = build_social_network(self.spec.network, trial.network_seed)
            agents, assignment = build_experimental_agents(
                self.spec.network.town_size,
                intervention,
                trial.assignment_seed,
            )
            context = TrialContext(
                trial, claims[trial.claim_id], intervention, network,
                tuple(agents), assignment,
            )
            outcomes = self.outcome_provider(context)
            self._validate_outcomes(outcomes)
            results.append(
                ExperimentalResult(
                    execution_index=trial.execution_index,
                    matched_trial_id=trial.matched_trial_id,
                    claim_id=trial.claim_id,
                    intervention_type=trial.intervention_type,
                    intervention_intensity=trial.intervention_intensity,
                    repetition=trial.repetition,
                    assignment_seed=trial.assignment_seed,
                    network_seed=trial.network_seed,
                    treated_positions=assignment.treated_positions,
                    outcomes=dict(outcomes),
                )
            )
        return tuple(results)

    def save(
        self,
        results: tuple[ExperimentalResult, ...],
        output_root: str | Path,
    ) -> Path:
        if len(results) != self.spec.planned_trials:
            raise ValueError("Dataset is incomplete and cannot be saved.")
        output = (
            Path(output_root)
            / self.spec.dataset_stage
            / f"{self.spec.name}-{self.spec.fingerprint}.json"
        )
        output.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "experiment_name": self.spec.name,
            "dataset_stage": self.spec.dataset_stage,
            "specification_fingerprint": self.spec.fingerprint,
            "results": [asdict(result) for result in results],
        }
        output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return output

    def _validate_stage(self) -> None:
        if self.spec.dataset_stage == "pilot":
            if self.preregistration_path is not None:
                raise ValueError("Pilot runs cannot use a confirmatory preregistration.")
            return
        if self.preregistration_path is None:
            raise ValueError("Confirmatory runs require a preregistration.")
        if not verify_preregistration(self.preregistration_path):
            raise ValueError("Confirmatory preregistration failed verification.")
        payload = json.loads(self.preregistration_path.read_text(encoding="utf-8"))
        if payload["specification_fingerprint"] != self.spec.fingerprint:
            raise ValueError("Preregistration does not match the experiment specification.")

    def _validate_outcomes(self, outcomes: dict[str, float]) -> None:
        if set(outcomes) != set(self.spec.outcomes):
            raise ValueError("Trial outcomes do not match the frozen outcome names.")
        if any(not isinstance(value, (int, float)) or not math.isfinite(value)
               for value in outcomes.values()):
            raise ValueError("Every trial outcome must be a finite number.")


def estimate_two_proportion_sample_size(
    baseline_rate: float,
    intervention_rate: float,
    *,
    alpha: float = 0.05,
    power: float = 0.8,
) -> int:
    """Approximate required observations per condition for two proportions."""
    if not 0.0 <= baseline_rate <= 1.0 or not 0.0 <= intervention_rate <= 1.0:
        raise ValueError("Rates must be between 0 and 1.")
    if baseline_rate == intervention_rate:
        raise ValueError("A nonzero expected effect is required.")
    if not 0.0 < alpha < 1.0 or not 0.0 < power < 1.0:
        raise ValueError("Alpha and power must be between 0 and 1.")
    average = (baseline_rate + intervention_rate) / 2
    z_alpha = NormalDist().inv_cdf(1 - alpha / 2)
    z_power = NormalDist().inv_cdf(power)
    numerator = (
        z_alpha * math.sqrt(2 * average * (1 - average))
        + z_power * math.sqrt(
            baseline_rate * (1 - baseline_rate)
            + intervention_rate * (1 - intervention_rate)
        )
    ) ** 2
    return math.ceil(numerator / (baseline_rate - intervention_rate) ** 2)
