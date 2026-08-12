from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
from typing import Literal

from mind_virus.experiment_spec import GeneralizedExperimentSpec


@dataclass(frozen=True)
class OutcomeDefinition:
    name: str
    unit: str
    calculation: str
    direction: Literal["lower", "higher", "two_sided"]


OUTCOME_REGISTRY = {
    "exposed_agents": OutcomeDefinition(
        "exposed_agents", "agents", "Count of unique agents who received the claim.", "lower"
    ),
    "maximum_generation": OutcomeDefinition(
        "maximum_generation", "generation", "Largest recorded transmission generation.", "lower"
    ),
    "repetition_rate": OutcomeDefinition(
        "repetition_rate", "proportion", "Repeating listeners divided by exposed listeners.", "lower"
    ),
    "belief_rate": OutcomeDefinition(
        "belief_rate", "proportion", "Believing listeners divided by exposed listeners.", "lower"
    ),
}


@dataclass(frozen=True)
class PreregisteredHypothesis:
    id: str
    intervention_type: str
    outcome: str
    prediction: str
    primary: bool = False

    def __post_init__(self) -> None:
        if not self.id.strip() or not self.prediction.strip():
            raise ValueError("Hypothesis ID and prediction cannot be empty.")


@dataclass(frozen=True)
class Preregistration:
    experiment_name: str
    specification_fingerprint: str
    hypotheses: tuple[PreregisteredHypothesis, ...]
    outcomes: tuple[OutcomeDefinition, ...]
    document_fingerprint: str


def freeze_preregistration(
    spec: GeneralizedExperimentSpec,
    hypotheses: tuple[PreregisteredHypothesis, ...],
    path: str | Path,
) -> Path:
    """Write one immutable confirmatory preregistration document."""
    if spec.dataset_stage != "confirmatory":
        raise ValueError("Only a confirmatory specification can be preregistered.")
    if not hypotheses:
        raise ValueError("At least one hypothesis is required.")
    if len({item.id for item in hypotheses}) != len(hypotheses):
        raise ValueError("Hypothesis IDs must be unique.")
    if sum(item.primary for item in hypotheses) != 1:
        raise ValueError("Exactly one hypothesis must be marked primary.")
    definitions: list[OutcomeDefinition] = []
    for outcome in spec.outcomes:
        if outcome not in OUTCOME_REGISTRY:
            raise ValueError(f"Outcome has no frozen definition: {outcome}")
        definitions.append(OUTCOME_REGISTRY[outcome])
    for hypothesis in hypotheses:
        if hypothesis.outcome not in spec.outcomes:
            raise ValueError("Every hypothesis outcome must be configured in the experiment.")
        if hypothesis.intervention_type not in {
            item.type for item in spec.interventions
        }:
            raise ValueError("Every hypothesis intervention must be configured.")

    core = {
        "experiment_name": spec.name,
        "specification_fingerprint": spec.fingerprint,
        "hypotheses": [asdict(item) for item in hypotheses],
        "outcomes": [asdict(item) for item in definitions],
    }
    document_fingerprint = hashlib.sha256(
        json.dumps(core, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    payload = {**core, "document_fingerprint": document_fingerprint}
    output = Path(path)
    if output.exists():
        existing = json.loads(output.read_text(encoding="utf-8"))
        if existing == payload:
            return output
        raise FileExistsError("A different preregistration already exists at this path.")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return output


def verify_preregistration(path: str | Path) -> bool:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    fingerprint = payload.pop("document_fingerprint", None)
    calculated = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return fingerprint == calculated
