from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
import random

from mind_virus.experiment_spec import GeneralizedExperimentSpec


@dataclass(frozen=True)
class PlannedTrial:
    execution_index: int
    matched_trial_id: str
    claim_id: str
    intervention_type: str
    intervention_intensity: float
    repetition: int
    assignment_seed: int
    network_seed: int
    dataset_stage: str
    specification_fingerprint: str


@dataclass(frozen=True)
class TrialManifest:
    experiment_name: str
    specification_fingerprint: str
    randomization_seed: int
    trials: tuple[PlannedTrial, ...]

    def __post_init__(self) -> None:
        if [trial.execution_index for trial in self.trials] != list(
            range(len(self.trials))
        ):
            raise ValueError("Trial execution indexes must be contiguous and ordered.")
        keys = {
            (trial.claim_id, trial.intervention_type, trial.intervention_intensity,
             trial.repetition)
            for trial in self.trials
        }
        if len(keys) != len(self.trials):
            raise ValueError("Trial manifest contains duplicate condition-trials.")

    def save(self, path: str | Path) -> Path:
        output = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")
        return output


def plan_matched_trials(spec: GeneralizedExperimentSpec) -> TrialManifest:
    """Expand and reproducibly randomize every configured condition-trial."""
    unrandomized: list[PlannedTrial] = []
    for claim in spec.claims:
        for repetition in range(spec.trials_per_condition):
            matched_id = f"{claim.id}:{repetition:04d}"
            assignment_seed = _stable_seed(spec.seed, matched_id, "assignment")
            network_seed = _stable_seed(spec.seed, matched_id, "network")
            for intervention in spec.interventions:
                unrandomized.append(
                    PlannedTrial(
                        execution_index=-1,
                        matched_trial_id=matched_id,
                        claim_id=claim.id,
                        intervention_type=intervention.type,
                        intervention_intensity=intervention.intensity,
                        repetition=repetition,
                        assignment_seed=assignment_seed,
                        network_seed=network_seed,
                        dataset_stage=spec.dataset_stage,
                        specification_fingerprint=spec.fingerprint,
                    )
                )
    randomization_seed = _stable_seed(spec.seed, spec.fingerprint, "execution-order")
    random.Random(randomization_seed).shuffle(unrandomized)
    trials = tuple(
        PlannedTrial(**{**asdict(trial), "execution_index": index})
        for index, trial in enumerate(unrandomized)
    )
    return TrialManifest(spec.name, spec.fingerprint, randomization_seed, trials)


def _stable_seed(seed: int, *parts: str) -> int:
    material = ":".join((str(seed), *parts)).encode("utf-8")
    return int.from_bytes(hashlib.sha256(material).digest()[:8], "big")
