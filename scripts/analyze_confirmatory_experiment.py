from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path
from typing import Any

from mind_virus.statistics import paired_bootstrap


DATASET = Path("results/phase5_confirmatory_experiment.jsonl")
OUTPUT = Path("results/phase6_confirmatory_analysis.json")

OUTCOMES = (
    "exposed_agents",
    "maximum_generation",
    "repetition_rate",
    "belief_rate",
)


def load_records(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as file:
        return [json.loads(line) for line in file if line.strip()]


def analyze_records(
    records: list[dict[str, Any]],
) -> dict[str, Any]:
    indexed = {
        (
            record["claim_id"],
            record["trial"],
            record["condition"],
        ): record
        for record in records
    }

    claim_ids = sorted(
        {record["claim_id"] for record in records}
    )
    trial_numbers = sorted(
        {record["trial"] for record in records}
    )

    expected_records = len(claim_ids) * len(trial_numbers) * 2
    if len(records) != expected_records:
        raise ValueError(
            f"Expected {expected_records} records, "
            f"but found {len(records)}."
        )

    results: dict[str, Any] = {
        "design": {
            "claims": len(claim_ids),
            "trials_per_condition_per_claim": len(trial_numbers),
            "condition_trials": len(records),
            "difference_direction": "skeptical minus baseline",
        },
        "by_claim": {},
        "pooled": {},
    }

    for claim_id in claim_ids:
        results["by_claim"][claim_id] = {}

        for outcome in OUTCOMES:
            baseline = [
                float(indexed[(claim_id, trial, "baseline")][outcome])
                for trial in trial_numbers
            ]
            skeptical = [
                float(indexed[(claim_id, trial, "skeptical")][outcome])
                for trial in trial_numbers
            ]

            results["by_claim"][claim_id][outcome] = asdict(
                paired_bootstrap(baseline, skeptical)
            )

    for outcome in OUTCOMES:
        baseline = []
        skeptical = []

        for claim_id in claim_ids:
            for trial in trial_numbers:
                baseline.append(
                    float(
                        indexed[
                            (claim_id, trial, "baseline")
                        ][outcome]
                    )
                )
                skeptical.append(
                    float(
                        indexed[
                            (claim_id, trial, "skeptical")
                        ][outcome]
                    )
                )

        results["pooled"][outcome] = asdict(
            paired_bootstrap(baseline, skeptical)
        )

    return results


def print_estimate(name: str, estimate: dict[str, Any]) -> None:
    print(
        f"  {name}: "
        f"baseline={estimate['baseline_mean']:.3f}, "
        f"skeptical={estimate['skeptical_mean']:.3f}, "
        f"difference={estimate['mean_difference']:+.3f}, "
        f"95% CI=[{estimate['confidence_interval_low']:+.3f}, "
        f"{estimate['confidence_interval_high']:+.3f}]"
    )


def main() -> None:
    records = load_records(DATASET)
    results = analyze_records(records)

    OUTPUT.parent.mkdir(exist_ok=True)
    OUTPUT.write_text(
        json.dumps(results, indent=2),
        encoding="utf-8",
    )

    print("PHASE 6: CONFIRMATORY STATISTICAL ANALYSIS")
    print("-" * 48)
    print(f"Condition-trials analyzed: {len(records)}")
    print("Difference means: skeptical minus baseline")
    print()

    for claim_id, claim_results in results["by_claim"].items():
        print(claim_id)
        for outcome, estimate in claim_results.items():
            print_estimate(outcome, estimate)
        print()

    print("POOLED ACROSS ALL CLAIMS")
    for outcome, estimate in results["pooled"].items():
        print_estimate(outcome, estimate)

    print()
    print(f"Analysis saved to: {OUTPUT}")
    print("No API requests were made.")


if __name__ == "__main__":
    main()
