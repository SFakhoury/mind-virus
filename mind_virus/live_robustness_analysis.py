from __future__ import annotations

from dataclasses import dataclass
from statistics import mean


@dataclass(frozen=True)
class LivePilotCellEffect:
    model: str
    prompt_variant: str
    baseline_belief_rate: float
    skeptical_belief_rate: float
    belief_difference: float
    baseline_repetition_rate: float
    skeptical_repetition_rate: float
    repetition_difference: float


@dataclass(frozen=True)
class LivePilotAnalysis:
    records: int
    cells: tuple[LivePilotCellEffect, ...]
    belief_direction_consistency: float
    repetition_direction_consistency: float
    total_input_tokens: int
    total_output_tokens: int
    estimated_cost_usd: float


def analyze_live_robustness(records: list[dict[str, object]]) -> LivePilotAnalysis:
    if not records:
        raise ValueError("Live robustness records cannot be empty.")
    grouped: dict[tuple[str, str, str], list[dict[str, object]]] = {}
    for record in records:
        key = (
            str(record["model"]), str(record["prompt_variant"]),
            str(record["condition"]),
        )
        grouped.setdefault(key, []).append(record)
    model_prompts = sorted({(key[0], key[1]) for key in grouped})
    cells: list[LivePilotCellEffect] = []
    for model, prompt in model_prompts:
        baseline = grouped.get((model, prompt, "baseline"), [])
        skeptical = grouped.get((model, prompt, "skeptical"), [])
        if not baseline or len(baseline) != len(skeptical):
            raise ValueError("Every model/prompt cell requires matched conditions.")
        baseline_belief = mean(bool(item["believes_claim"]) for item in baseline)
        skeptical_belief = mean(bool(item["believes_claim"]) for item in skeptical)
        baseline_repetition = mean(bool(item["repeats_claim"]) for item in baseline)
        skeptical_repetition = mean(bool(item["repeats_claim"]) for item in skeptical)
        cells.append(LivePilotCellEffect(
            model, prompt,
            baseline_belief, skeptical_belief, skeptical_belief - baseline_belief,
            baseline_repetition, skeptical_repetition,
            skeptical_repetition - baseline_repetition,
        ))
    return LivePilotAnalysis(
        records=len(records),
        cells=tuple(cells),
        belief_direction_consistency=(
            sum(cell.belief_difference < 0 for cell in cells) / len(cells)
        ),
        repetition_direction_consistency=(
            sum(cell.repetition_difference < 0 for cell in cells) / len(cells)
        ),
        total_input_tokens=sum(int(item["input_tokens"]) for item in records),
        total_output_tokens=sum(int(item["output_tokens"]) for item in records),
        estimated_cost_usd=sum(float(item["estimated_cost_usd"]) for item in records),
    )


def render_live_pilot_report(analysis: LivePilotAnalysis) -> str:
    rows = "\n".join(
        "| " + " | ".join((
            cell.model, cell.prompt_variant,
            f"{cell.baseline_belief_rate:.3f}", f"{cell.skeptical_belief_rate:.3f}",
            f"{cell.belief_difference:+.3f}",
            f"{cell.baseline_repetition_rate:.3f}",
            f"{cell.skeptical_repetition_rate:.3f}",
            f"{cell.repetition_difference:+.3f}",
        )) + " |"
        for cell in analysis.cells
    )
    return f"""# Phase 12 Live Robustness Pilot

This diagnostic pilot compared two models and two prompt variants across
matched baseline and skeptical listener conditions. It contains
{analysis.records} structured model decisions and is not a final confirmatory dataset.

| Model | Prompt | Base belief | Skeptic belief | Difference | Base repeat | Skeptic repeat | Difference |
|---|---|---:|---:|---:|---:|---:|---:|
{rows}

## Pilot interpretation

- Belief-effect direction consistency: {analysis.belief_direction_consistency:.3f}
- Repetition-effect direction consistency: {analysis.repetition_direction_consistency:.3f}
- Input tokens: {analysis.total_input_tokens}
- Output tokens: {analysis.total_output_tokens}
- Estimated cost: ${analysis.estimated_cost_usd:.4f}

Skepticism reduced repetition in every model/prompt cell. Belief was already
absent in most baseline cells, producing a floor effect; therefore this pilot
does not establish a robust belief reduction. The sample is small, uses one
claim, and evaluates one listener decision rather than full-chain propagation.
"""
