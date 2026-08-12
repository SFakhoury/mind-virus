from __future__ import annotations

from dataclasses import dataclass
from math import comb
from statistics import mean

from mind_virus.statistics import paired_bootstrap


@dataclass(frozen=True)
class ConfirmatoryEffect:
    outcome: str
    pairs: int
    baseline_rate: float
    skeptical_rate: float
    difference: float
    confidence_interval_low: float
    confidence_interval_high: float
    discordant_lower: int
    discordant_higher: int
    exact_p_value: float


@dataclass(frozen=True)
class ConfirmatoryRobustnessAnalysis:
    records: int
    cells: int
    primary: ConfirmatoryEffect
    secondary: ConfirmatoryEffect
    cell_effects: tuple[dict[str, object], ...]
    estimated_cost_usd: float


def _exact_mcnemar(lower: int, higher: int) -> float:
    discordant = lower + higher
    if discordant == 0:
        return 1.0
    tail = sum(comb(discordant, k) for k in range(min(lower, higher) + 1))
    return min(1.0, 2.0 * tail / (2 ** discordant))


def _effect(pairs: list[tuple[dict[str, object], dict[str, object]]], outcome: str) -> ConfirmatoryEffect:
    baseline = [float(bool(base[outcome])) for base, _ in pairs]
    skeptical = [float(bool(skeptic[outcome])) for _, skeptic in pairs]
    estimate = paired_bootstrap(baseline, skeptical, iterations=10_000, seed=2026)
    lower = sum(base == 1.0 and skeptic == 0.0 for base, skeptic in zip(baseline, skeptical))
    higher = sum(base == 0.0 and skeptic == 1.0 for base, skeptic in zip(baseline, skeptical))
    return ConfirmatoryEffect(outcome, len(pairs), mean(baseline), mean(skeptical),
        mean(skeptical) - mean(baseline), estimate.confidence_interval_low,
        estimate.confidence_interval_high, lower, higher, _exact_mcnemar(lower, higher))


def analyze_confirmatory_robustness(records: list[dict[str, object]]) -> ConfirmatoryRobustnessAnalysis:
    if len(records) != 648:
        raise ValueError("Confirmatory analysis requires exactly 648 records.")
    keyed = {(str(item["claim_id"]), str(item["model"]), str(item["prompt_variant"]),
              int(item["trial"]), str(item["condition"])): item for item in records}
    strata = sorted({key[:3] for key in keyed})
    pairs: list[tuple[dict[str, object], dict[str, object]]] = []
    cells: list[dict[str, object]] = []
    for claim, model, prompt in strata:
        cell_pairs = []
        for trial in range(27):
            try:
                cell_pairs.append((keyed[(claim, model, prompt, trial, "baseline")], keyed[(claim, model, prompt, trial, "skeptical")]))
            except KeyError as error:
                raise ValueError("Every confirmatory trial requires matched conditions.") from error
        pairs.extend(cell_pairs)
        repeat = _effect(cell_pairs, "repeats_claim")
        belief = _effect(cell_pairs, "believes_claim")
        cells.append({"claim_id": claim, "model": model, "prompt_variant": prompt,
                      "repetition_difference": repeat.difference, "belief_difference": belief.difference})
    if len(strata) != 12:
        raise ValueError("Confirmatory analysis requires exactly 12 cells.")
    return ConfirmatoryRobustnessAnalysis(len(records), len(strata),
        _effect(pairs, "repeats_claim"), _effect(pairs, "believes_claim"), tuple(cells),
        sum(float(item["estimated_cost_usd"]) for item in records))


def render_confirmatory_robustness_report(result: ConfirmatoryRobustnessAnalysis) -> str:
    def line(effect: ConfirmatoryEffect) -> str:
        return (f"Baseline {effect.baseline_rate:.3f}; skeptical {effect.skeptical_rate:.3f}; "
                f"difference {effect.difference:+.3f}; 95% bootstrap CI "
                f"[{effect.confidence_interval_low:+.3f}, {effect.confidence_interval_high:+.3f}]; "
                f"exact paired p={effect.exact_p_value:.4g}.")
    rows = "\n".join(f'| {c["claim_id"]} | {c["model"]} | {c["prompt_variant"]} | {c["repetition_difference"]:+.3f} | {c["belief_difference"]:+.3f} |' for c in result.cell_effects)
    return f"""# Phase 12 Confirmatory Robustness Results

This preregistered confirmatory dataset contains {result.records} live model decisions across {result.cells} claim/model/prompt cells, with 27 matched trials per condition in every cell. Effects are skeptical minus baseline.

## Primary outcome: repetition

{line(result.primary)}

## Secondary outcome: belief

{line(result.secondary)}

| Claim | Model | Prompt | Repetition difference | Belief difference |
|---|---|---|---:|---:|
{rows}

## Interpretation

Negative differences indicate that skepticism reduced the outcome. Repetition and belief are reported separately because an agent may repeat an unverified claim without believing it. Exact McNemar tests use matched binary decisions; confidence intervals are paired bootstrap intervals. Estimated API cost: ${result.estimated_cost_usd:.4f}.
"""
