from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Any

from mind_virus.decision import TransmissionDecision
from mind_virus.live_robustness_pilot import LiveRobustnessPlan, PRICING, PROMPTS


CLAIMS = (
    ("bakery_free_bread", "I heard the bakery is giving away free bread today."),
    ("library_early_closure", "I heard the library is closing early because of a pipe leak."),
    ("bus_route_change", "I heard the market bus stop is closed because of road work."),
)


@dataclass(frozen=True)
class MultiClaimRobustnessPlan:
    base: LiveRobustnessPlan = LiveRobustnessPlan()
    claims: tuple[tuple[str, str], ...] = CLAIMS
    cost_ceiling_usd: float = 0.20

    @property
    def planned_calls(self) -> int:
        return self.base.planned_calls * len(self.claims)

    @property
    def estimated_cost_usd(self) -> float:
        return self.base.estimated_cost_usd * len(self.claims)

    def validate(self) -> None:
        self.base.validate()
        if not self.claims or any(not claim_id.strip() or not message.strip()
                                  for claim_id, message in self.claims):
            raise ValueError("Every robustness claim requires an ID and message.")
        if len({claim_id for claim_id, _ in self.claims}) != len(self.claims):
            raise ValueError("Robustness claim IDs must be unique.")
        if self.estimated_cost_usd > self.cost_ceiling_usd:
            raise ValueError("Estimated multi-claim cost exceeds the hard ceiling.")


def collect_multi_claim_robustness(
    plan: MultiClaimRobustnessPlan,
    output_path: str | Path,
    *,
    client: Any,
) -> list[dict[str, object]]:
    plan.validate()
    output = Path(output_path)
    records = _load(output)
    completed = {record["key"] for record in records}
    base = plan.base
    for claim_id, claim_message in plan.claims:
        for model in base.models:
            for prompt_name in base.prompt_variants:
                for condition in base.conditions:
                    for trial in range(base.trials_per_cell):
                        key = f"{claim_id}:{model}:{prompt_name}:{condition}:{trial}"
                        if key in completed:
                            continue
                        input_price, output_price = PRICING[model]
                        reservation = (
                            base.estimated_input_tokens * input_price
                            + base.estimated_output_tokens * output_price
                        ) / 1_000_000
                        spent = sum(float(item["estimated_cost_usd"]) for item in records)
                        if spent + reservation > plan.cost_ceiling_usd:
                            raise RuntimeError("The next call would exceed the cost ceiling.")
                        personality = "Open and socially attentive."
                        if condition == "skeptical":
                            personality += (
                                " Requires corroborating evidence before believing or "
                                "repeating unsupported claims."
                            )
                        response = client.responses.parse(
                            model=model,
                            instructions=(
                                "Simulate a fictional listener in a controlled research "
                                "experiment. Do not invent evidence. " + PROMPTS[prompt_name]
                            ),
                            input=(
                                f"Listener personality: {personality}\nSpeaker: Alice\n"
                                f"Claim: {claim_message}\n"
                                "Relevant memories: No direct evidence is available."
                            ),
                            text_format=TransmissionDecision,
                            max_output_tokens=base.estimated_output_tokens,
                            reasoning={"effort": "none"},
                        )
                        decision = response.output_parsed
                        if decision is None:
                            raise ValueError("Model returned no structured decision.")
                        usage = getattr(response, "usage", None)
                        input_tokens = int(getattr(usage, "input_tokens", 0))
                        output_tokens = int(getattr(usage, "output_tokens", 0))
                        cost = (
                            input_tokens * input_price + output_tokens * output_price
                        ) / 1_000_000
                        records.append({
                            "key": key, "claim_id": claim_id, "model": model,
                            "prompt_variant": prompt_name, "condition": condition,
                            "trial": trial, "believes_claim": decision.believes_claim,
                            "repeats_claim": decision.repeats_claim,
                            "belief_confidence": decision.belief_confidence,
                            "reason": decision.reason,
                            "remembered_message": decision.remembered_message,
                            "input_tokens": input_tokens, "output_tokens": output_tokens,
                            "estimated_cost_usd": cost,
                        })
                        _save(output, plan, records)
    return records


def _load(path: Path) -> list[dict[str, object]]:
    return [] if not path.exists() else list(
        json.loads(path.read_text(encoding="utf-8"))["records"]
    )


def _save(path: Path, plan: MultiClaimRobustnessPlan,
          records: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps({"plan": asdict(plan), "records": records}, indent=2),
        encoding="utf-8",
    )
    temporary.replace(path)
