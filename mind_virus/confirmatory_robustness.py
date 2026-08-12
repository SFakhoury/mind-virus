from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
from typing import Any

from mind_virus.live_robustness_pilot import LiveRobustnessPlan
from mind_virus.multi_claim_robustness_pilot import (
    CLAIMS, MultiClaimRobustnessPlan, collect_multi_claim_robustness,
)


@dataclass(frozen=True)
class ConfirmatoryRobustnessProtocol:
    plan: MultiClaimRobustnessPlan = MultiClaimRobustnessPlan(
        base=LiveRobustnessPlan(
            trials_per_cell=27,
            estimated_output_tokens=200,
            cost_ceiling_usd=0.50,
        ),
        claims=CLAIMS,
        cost_ceiling_usd=1.50,
    )
    primary_outcome: str = "repeats_claim"
    secondary_outcome: str = "believes_claim"
    expected_direction: str = "skeptical_lower_than_baseline"
    alpha: float = 0.05
    target_power: float = 0.80
    sample_size_basis: str = (
        "27 trials per condition detects approximately 0.25 versus 0.00 "
        "proportions at two-sided alpha 0.05 and power 0.80."
    )
    dataset_stage: str = "confirmatory"

    @property
    def planned_calls(self) -> int:
        return self.plan.planned_calls

    @property
    def fingerprint(self) -> str:
        material = json.dumps(asdict(self), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(material.encode("utf-8")).hexdigest()

    def validate(self) -> None:
        self.plan.validate()
        if self.planned_calls != 648:
            raise ValueError("Confirmatory protocol must contain exactly 648 calls.")
        if self.primary_outcome == self.secondary_outcome:
            raise ValueError("Primary and secondary outcomes must differ.")
        if self.dataset_stage != "confirmatory":
            raise ValueError("This protocol is restricted to confirmatory data.")

    def freeze(self, path: str | Path) -> Path:
        self.validate()
        output = Path(path)
        payload = json.loads(json.dumps({
            **asdict(self),
            "planned_calls": self.planned_calls,
            "fingerprint": self.fingerprint,
        }))
        if output.exists():
            existing = json.loads(output.read_text(encoding="utf-8"))
            if existing != payload:
                raise FileExistsError("A different frozen protocol already exists.")
            return output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return output


def collect_confirmatory_robustness(
    protocol: ConfirmatoryRobustnessProtocol,
    protocol_path: str | Path,
    output_path: str | Path,
    *,
    client: Any,
) -> list[dict[str, object]]:
    protocol.validate()
    frozen = json.loads(Path(protocol_path).read_text(encoding="utf-8"))
    if frozen.get("fingerprint") != protocol.fingerprint:
        raise ValueError("Frozen protocol does not match the collector configuration.")
    output = Path(output_path)
    if output.exists():
        saved = json.loads(output.read_text(encoding="utf-8"))
        expected_plan = json.loads(json.dumps(asdict(protocol.plan)))
        if saved.get("plan") != expected_plan:
            raise ValueError("Existing checkpoint was created by a different plan.")
    return collect_multi_claim_robustness(protocol.plan, output, client=client)
