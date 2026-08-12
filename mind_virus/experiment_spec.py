from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
from typing import Literal


NetworkType = Literal["chain", "ring", "small_world", "complete"]
EvidenceCondition = Literal["none", "correction", "supporting"]
InterventionType = Literal["none", "skepticism", "fact_check", "inoculation"]


@dataclass(frozen=True)
class NetworkSpec:
    structure: NetworkType
    town_size: int
    rewiring_probability: float = 0.0

    def __post_init__(self) -> None:
        if self.structure not in {"chain", "ring", "small_world", "complete"}:
            raise ValueError("Unsupported social-network structure.")
        if self.town_size < 2:
            raise ValueError("Town size must be at least 2.")
        if not 0.0 <= self.rewiring_probability <= 1.0:
            raise ValueError("Rewiring probability must be between 0 and 1.")
        if self.structure != "small_world" and self.rewiring_probability != 0.0:
            raise ValueError("Rewiring applies only to a small-world network.")


@dataclass(frozen=True)
class ClaimSpec:
    id: str
    topic: str
    message: str
    evidence_condition: EvidenceCondition = "none"
    evidence: str | None = None

    def __post_init__(self) -> None:
        if not self.id.strip() or not self.topic.strip() or not self.message.strip():
            raise ValueError("Claim ID, topic, and message cannot be empty.")
        if self.evidence_condition not in {"none", "correction", "supporting"}:
            raise ValueError("Unsupported evidence condition.")
        if self.evidence_condition == "none" and self.evidence is not None:
            raise ValueError("An evidence-free claim cannot include evidence text.")
        if self.evidence_condition != "none" and not (self.evidence or "").strip():
            raise ValueError("This evidence condition requires evidence text.")


@dataclass(frozen=True)
class InterventionSpec:
    type: InterventionType
    intensity: float = 0.0

    def __post_init__(self) -> None:
        if self.type not in {"none", "skepticism", "fact_check", "inoculation"}:
            raise ValueError("Unsupported intervention type.")
        if not 0.0 <= self.intensity <= 1.0:
            raise ValueError("Intervention intensity must be between 0 and 1.")
        if self.type == "none" and self.intensity != 0.0:
            raise ValueError("The control intervention must have zero intensity.")
        if self.type != "none" and self.intensity == 0.0:
            raise ValueError("An active intervention must have positive intensity.")


@dataclass(frozen=True)
class GeneralizedExperimentSpec:
    name: str
    seed: int
    trials_per_condition: int
    network: NetworkSpec
    claims: tuple[ClaimSpec, ...]
    interventions: tuple[InterventionSpec, ...]
    outcomes: tuple[str, ...] = (
        "exposed_agents", "maximum_generation", "repetition_rate", "belief_rate"
    )
    dataset_stage: Literal["pilot", "confirmatory"] = "pilot"

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Experiment name cannot be empty.")
        if self.trials_per_condition < 1:
            raise ValueError("Trials per condition must be at least 1.")
        if not self.claims:
            raise ValueError("At least one claim is required.")
        if len({claim.id for claim in self.claims}) != len(self.claims):
            raise ValueError("Claim IDs must be unique.")
        if not self.interventions:
            raise ValueError("At least one intervention is required.")
        conditions = {(item.type, item.intensity) for item in self.interventions}
        if len(conditions) != len(self.interventions):
            raise ValueError("Intervention conditions must be unique.")
        if not self.outcomes or any(not item.strip() for item in self.outcomes):
            raise ValueError("At least one named outcome is required.")
        if len(set(self.outcomes)) != len(self.outcomes):
            raise ValueError("Outcome names must be unique.")
        if self.dataset_stage not in {"pilot", "confirmatory"}:
            raise ValueError("Dataset stage must be pilot or confirmatory.")

    @property
    def planned_trials(self) -> int:
        return len(self.claims) * len(self.interventions) * self.trials_per_condition

    @property
    def fingerprint(self) -> str:
        encoded = json.dumps(asdict(self), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(encoded.encode("utf-8")).hexdigest()[:16]

    def save(self, path: str | Path) -> Path:
        output = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)
        payload = asdict(self)
        payload["fingerprint"] = self.fingerprint
        payload["planned_trials"] = self.planned_trials
        output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return output

    @classmethod
    def load(cls, path: str | Path) -> "GeneralizedExperimentSpec":
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        expected_fingerprint = payload.pop("fingerprint", None)
        payload.pop("planned_trials", None)
        payload["network"] = NetworkSpec(**payload["network"])
        payload["claims"] = tuple(ClaimSpec(**item) for item in payload["claims"])
        payload["interventions"] = tuple(
            InterventionSpec(**item) for item in payload["interventions"]
        )
        payload["outcomes"] = tuple(payload["outcomes"])
        spec = cls(**payload)
        if expected_fingerprint is not None and expected_fingerprint != spec.fingerprint:
            raise ValueError("Experiment specification fingerprint does not match.")
        return spec
