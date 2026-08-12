from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt


INPUT = Path("results/phase6_confirmatory_analysis.json")
FIGURES = Path("docs/figures")
REPORT = Path("docs/confirmatory-results.md")

CLAIM_LABELS = {
    "bakery_free_bread": "Bakery free bread",
    "library_early_closure": "Library early closure",
    "bus_route_change": "Bus route change",
}


def load_analysis() -> dict:
    return json.loads(INPUT.read_text(encoding="utf-8"))


def create_belief_chart(analysis: dict) -> None:
    claims = list(analysis["by_claim"])
    labels = [CLAIM_LABELS.get(claim, claim) for claim in claims]

    baseline = [
        analysis["by_claim"][claim]["belief_rate"]["baseline_mean"]
        for claim in claims
    ]
    skeptical = [
        analysis["by_claim"][claim]["belief_rate"]["skeptical_mean"]
        for claim in claims
    ]

    positions = list(range(len(claims)))
    width = 0.36

    fig, axis = plt.subplots(figsize=(9, 5.5))

    axis.bar(
        [position - width / 2 for position in positions],
        baseline,
        width,
        label="Baseline",
        color="#ef8354",
    )
    axis.bar(
        [position + width / 2 for position in positions],
        skeptical,
        width,
        label="Skeptical treatment",
        color="#4f6d9b",
    )

    axis.set_title("Belief Rate by Claim and Condition")
    axis.set_ylabel("Average belief rate")
    axis.set_xticks(positions, labels)
    axis.set_ylim(0, max(0.35, max(baseline + skeptical) + 0.08))
    axis.legend()
    axis.grid(axis="y", alpha=0.25)

    fig.tight_layout()
    fig.savefig(
        FIGURES / "confirmatory-belief-rates.png",
        dpi=180,
    )
    plt.close(fig)


def create_effect_chart(analysis: dict) -> None:
    claim_ids = list(analysis["by_claim"])
    labels = [
        CLAIM_LABELS.get(claim_id, claim_id)
        for claim_id in claim_ids
    ] + ["Pooled"]

    estimates = [
        analysis["by_claim"][claim_id]["belief_rate"]
        for claim_id in claim_ids
    ] + [analysis["pooled"]["belief_rate"]]

    differences = [
        estimate["mean_difference"]
        for estimate in estimates
    ]
    lower_errors = [
        difference - estimate["confidence_interval_low"]
        for difference, estimate in zip(differences, estimates)
    ]
    upper_errors = [
        estimate["confidence_interval_high"] - difference
        for difference, estimate in zip(differences, estimates)
    ]

    positions = list(range(len(labels)))

    fig, axis = plt.subplots(figsize=(9, 5.5))

    axis.errorbar(
        differences,
        positions,
        xerr=[lower_errors, upper_errors],
        fmt="o",
        color="#263d5a",
        ecolor="#4f6d9b",
        capsize=5,
        markersize=7,
    )

    axis.axvline(0, color="#222222", linestyle="--", linewidth=1)
    axis.set_yticks(positions, labels)
    axis.invert_yaxis()
    axis.set_xlabel(
        "Change in belief rate (skeptical minus baseline)"
    )
    axis.set_title("Estimated Skeptical-Treatment Effect on Belief")
    axis.grid(axis="x", alpha=0.25)

    fig.tight_layout()
    fig.savefig(
        FIGURES / "confirmatory-belief-effects.png",
        dpi=180,
    )
    plt.close(fig)


def create_report(analysis: dict) -> None:
    pooled = analysis["pooled"]
    belief = pooled["belief_rate"]
    repetition = pooled["repetition_rate"]
    exposure = pooled["exposed_agents"]
    generation = pooled["maximum_generation"]

    report = f"""# Confirmatory Experiment Results

## Experiment design

The confirmatory dataset contains:

- 3 misinformation claims
- 20 matched trials per condition for each claim
- 2 conditions: baseline and skeptical treatment
- 120 condition-trials
- 360 model calls

All treatment effects are calculated as skeptical minus baseline. Negative
values therefore indicate that the skeptical treatment reduced an outcome.

## Primary outcome: exposure

Average exposure was {exposure["baseline_mean"]:.3f} agents in the baseline
condition and {exposure["skeptical_mean"]:.3f} agents in the skeptical
condition.

The estimated paired difference was
{exposure["mean_difference"]:+.3f}, with a 95% bootstrap interval of
[{exposure["confidence_interval_low"]:+.3f},
{exposure["confidence_interval_high"]:+.3f}].

The experiment therefore found no reduction in how many agents encountered
the claims.

## Belief

The pooled belief rate decreased from
{belief["baseline_mean"]:.3f} in the baseline condition to
{belief["skeptical_mean"]:.3f} under the skeptical treatment.

The estimated paired difference was
{belief["mean_difference"]:+.3f}, with a 95% bootstrap interval of
[{belief["confidence_interval_low"]:+.3f},
{belief["confidence_interval_high"]:+.3f}].

Within this simulated experiment, skeptical prompting reduced belief even
though it did not stop agents from encountering the claims.

![Belief rates](figures/confirmatory-belief-rates.png)

![Belief effects](figures/confirmatory-belief-effects.png)

## Repetition and propagation depth

The pooled repetition rate changed from
{repetition["baseline_mean"]:.3f} to
{repetition["skeptical_mean"]:.3f}. The paired difference was
{repetition["mean_difference"]:+.3f}, with a 95% interval of
[{repetition["confidence_interval_low"]:+.3f},
{repetition["confidence_interval_high"]:+.3f}].

Maximum generation was {generation["baseline_mean"]:.3f} in the baseline
condition and {generation["skeptical_mean"]:.3f} under treatment.

These results suggest that agents could repeat a claim without believing it.
The treatment influenced acceptance more strongly than transmission.

## Interpretation

The evidence does not support the simple hypothesis that skeptical agents
necessarily stop misinformation from travelling through a social chain.

Instead, it supports a more nuanced result: skeptical agents may continue
discussing unverified information while assigning it lower credibility.

This distinction between propagation and belief is important. Measuring only
whether a message was repeated would have missed the treatment's strongest
observed effect.

## Limitations

- The experiment used one language model.
- The simulated town used short, linear communication chains.
- Only three claims were included.
- Agent behavior was generated from prompts rather than human participants.
- Repetition rates were close to their maximum, creating a ceiling effect.
- Bootstrap intervals describe variation in this simulated dataset and should
  not be interpreted as evidence about real human populations.
"""

    REPORT.write_text(report, encoding="utf-8")


def main() -> None:
    analysis = load_analysis()
    FIGURES.mkdir(parents=True, exist_ok=True)

    create_belief_chart(analysis)
    create_effect_chart(analysis)
    create_report(analysis)

    print("PHASE 6: RESEARCH FIGURES AND RESULTS")
    print("-" * 44)
    print("Created:")
    print("  docs/figures/confirmatory-belief-rates.png")
    print("  docs/figures/confirmatory-belief-effects.png")
    print("  docs/confirmatory-results.md")
    print()
    print("No API requests were made.")


if __name__ == "__main__":
    main()
