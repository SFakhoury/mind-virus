from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Any

from mind_virus.decision import TransmissionDecision


PRICING = {
    "gpt-5.6-luna": (0.20, 1.20),
    "gpt-5.6-terra": (2.00, 12.00),
}
PROMPTS = {
    "neutral": "Evaluate the claim from the listener's stated perspective.",
    "evidence_explicit": (
        "Evaluate the claim from the listener's stated perspective. Keep hearsay, "
        "direct evidence, belief, and willingness to repeat strictly separate."
    ),
}


@dataclass(frozen=True)
class LiveRobustnessPlan:
    models: tuple[str, ...] = ("gpt-5.6-luna", "gpt-5.6-terra")
    prompt_variants: tuple[str, ...] = ("neutral", "evidence_explicit")
    conditions: tuple[str, ...] = ("baseline", "skeptical")
    trials_per_cell: int = 4
    estimated_input_tokens: int = 500
    estimated_output_tokens: int = 100
    cost_ceiling_usd: float = 0.10

    @property
    def planned_calls(self) -> int:
        return (
            len(self.models) * len(self.prompt_variants)
            * len(self.conditions) * self.trials_per_cell
        )

    @property
    def estimated_cost_usd(self) -> float:
        total = 0.0
        calls_per_model = (
            len(self.prompt_variants) * len(self.conditions) * self.trials_per_cell
        )
        for model in self.models:
            input_price, output_price = PRICING[model]
            total += calls_per_model * (
                self.estimated_input_tokens * input_price
                + self.estimated_output_tokens * output_price
            ) / 1_000_000
        return total

    def validate(self) -> None:
        if self.trials_per_cell < 1:
            raise ValueError("Trials per cell must be positive.")
        if any(model not in PRICING for model in self.models):
            raise ValueError("Every model requires explicit pricing.")
        if any(prompt not in PROMPTS for prompt in self.prompt_variants):
            raise ValueError("Unknown robustness prompt variant.")
        if self.estimated_cost_usd > self.cost_ceiling_usd:
            raise ValueError("Estimated robustness cost exceeds the hard ceiling.")


def collect_live_robustness_pilot(
    plan: LiveRobustnessPlan,
    output_path: str | Path,
    *,
    client: Any,
) -> list[dict[str, object]]:
    plan.validate()
    output = Path(output_path)
    records = _load_records(output)
    completed = {record["key"] for record in records}
    for model in plan.models:
        for prompt_name in plan.prompt_variants:
            for condition in plan.conditions:
                for trial in range(plan.trials_per_cell):
                    key = f"{model}:{prompt_name}:{condition}:{trial}"
                    if key in completed:
                        continue
                    input_price, output_price = PRICING[model]
                    reserved_cost = (
                        plan.estimated_input_tokens * input_price
                        + plan.estimated_output_tokens * output_price
                    ) / 1_000_000
                    observed_cost = sum(
                        float(item["estimated_cost_usd"]) for item in records
                    )
                    if observed_cost + reserved_cost > plan.cost_ceiling_usd:
                        raise RuntimeError(
                            "The next request would exceed the robustness cost ceiling."
                        )
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
                            f"Listener personality: {personality}\n"
                            "Speaker: Alice\n"
                            "Claim: I heard the bakery is giving away free bread today.\n"
                            "Relevant memories: No direct evidence is available."
                        ),
                        text_format=TransmissionDecision,
                        max_output_tokens=plan.estimated_output_tokens,
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
                        "key": key, "model": model, "prompt_variant": prompt_name,
                        "condition": condition, "trial": trial,
                        "believes_claim": decision.believes_claim,
                        "repeats_claim": decision.repeats_claim,
                        "belief_confidence": decision.belief_confidence,
                        "reason": decision.reason,
                        "remembered_message": decision.remembered_message,
                        "input_tokens": input_tokens, "output_tokens": output_tokens,
                        "estimated_cost_usd": cost,
                    })
                    _save_records(output, plan, records)
                    if sum(float(item["estimated_cost_usd"]) for item in records) > plan.cost_ceiling_usd:
                        raise RuntimeError("Observed usage exceeded the robustness cost ceiling.")
    return records


def _load_records(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []
    return list(json.loads(path.read_text(encoding="utf-8"))["records"])


def _save_records(path: Path, plan: LiveRobustnessPlan, records: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps({"plan": asdict(plan), "records": records}, indent=2), encoding="utf-8")
    temporary.replace(path)
