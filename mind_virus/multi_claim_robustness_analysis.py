from __future__ import annotations

from dataclasses import dataclass
from statistics import mean


@dataclass(frozen=True)
class MultiClaimCellEffect:
    claim_id: str
    model: str
    prompt_variant: str
    belief_difference: float
    repetition_difference: float
    baseline_belief_rate: float
    baseline_repetition_rate: float
    skeptical_belief_rate: float
    skeptical_repetition_rate: float


@dataclass(frozen=True)
class MultiClaimRobustnessAnalysis:
    records: int
    cells: tuple[MultiClaimCellEffect, ...]
    belief_reduction_cells: int
    repetition_reduction_cells: int
    belief_floor_cells: int
    repetition_floor_cells: int
    contradictory_belief_cells: int
    contradictory_repetition_cells: int
    estimated_cost_usd: float


def analyze_multi_claim_robustness(
    records: list[dict[str, object]],
) -> MultiClaimRobustnessAnalysis:
    if not records:
        raise ValueError("Multi-claim robustness records cannot be empty.")
    grouped: dict[tuple[str, str, str, str], list[dict[str, object]]] = {}
    for item in records:
        key = tuple(str(item[field]) for field in (
            "claim_id", "model", "prompt_variant", "condition"
        ))
        grouped.setdefault(key, []).append(item)
    cell_keys = sorted({key[:3] for key in grouped})
    cells: list[MultiClaimCellEffect] = []
    for claim, model, prompt in cell_keys:
        baseline = grouped.get((claim, model, prompt, "baseline"), [])
        skeptical = grouped.get((claim, model, prompt, "skeptical"), [])
        if not baseline or len(baseline) != len(skeptical):
            raise ValueError("Every multi-claim cell requires matched conditions.")
        base_belief = mean(bool(item["believes_claim"]) for item in baseline)
        skeptic_belief = mean(bool(item["believes_claim"]) for item in skeptical)
        base_repeat = mean(bool(item["repeats_claim"]) for item in baseline)
        skeptic_repeat = mean(bool(item["repeats_claim"]) for item in skeptical)
        cells.append(MultiClaimCellEffect(
            claim, model, prompt,
            skeptic_belief - base_belief, skeptic_repeat - base_repeat,
            base_belief, base_repeat, skeptic_belief, skeptic_repeat,
        ))
    return MultiClaimRobustnessAnalysis(
        records=len(records), cells=tuple(cells),
        belief_reduction_cells=sum(item.belief_difference < 0 for item in cells),
        repetition_reduction_cells=sum(item.repetition_difference < 0 for item in cells),
        belief_floor_cells=sum(item.baseline_belief_rate == 0 for item in cells),
        repetition_floor_cells=sum(item.baseline_repetition_rate == 0 for item in cells),
        contradictory_belief_cells=sum(item.belief_difference > 0 for item in cells),
        contradictory_repetition_cells=sum(item.repetition_difference > 0 for item in cells),
        estimated_cost_usd=sum(float(item["estimated_cost_usd"]) for item in records),
    )


def render_multi_claim_report(analysis: MultiClaimRobustnessAnalysis) -> str:
    rows = "\n".join(
        f"| {item.claim_id} | {item.model} | {item.prompt_variant} | "
        f"{item.belief_difference:+.3f} | {item.repetition_difference:+.3f} |"
        for item in analysis.cells
    )
    return f"""# Phase 12 Multi-Claim Robustness Pilot

This diagnostic dataset contains {analysis.records} live structured decisions
across three claims, two models, two prompts, and matched baseline/skeptical
conditions. Each cell has four trials; it is not final confirmatory evidence.

| Claim | Model | Prompt | Belief difference | Repetition difference |
|---|---|---|---:|---:|
{rows}

## Summary

- Cells with lower belief: {analysis.belief_reduction_cells}/{len(analysis.cells)}
- Belief floor cells: {analysis.belief_floor_cells}/{len(analysis.cells)}
- Cells with lower repetition: {analysis.repetition_reduction_cells}/{len(analysis.cells)}
- Repetition floor cells: {analysis.repetition_floor_cells}/{len(analysis.cells)}
- Cells contradicting the expected belief direction: {analysis.contradictory_belief_cells}
- Cells contradicting the expected repetition direction: {analysis.contradictory_repetition_cells}
- Estimated API cost: ${analysis.estimated_cost_usd:.4f}

Skeptical listeners repeated no tested claim. Reductions were observable only
where baseline agents had a nonzero rate; zero-baseline cells are floor effects,
not evidence that skepticism failed or reversed direction. Model and prompt
choice materially changed baseline behavior. This small direct-decision pilot
does not replace a powered, full-chain confirmatory robustness experiment.
"""
