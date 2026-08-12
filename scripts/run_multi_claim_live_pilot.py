from collections import defaultdict
from dataclasses import asdict
import json
from pathlib import Path
from statistics import mean

from mind_virus.calibrated_pilot import (
    run_calibrated_pilot,
)
from mind_virus.config import ExperimentConfig
from mind_virus.decision import OpenAIDecisionMaker
from mind_virus.seed_claims import SEED_CLAIMS


def summarize(result, condition, trials):
    selected = [
        record
        for record in result.records
        if record.condition == condition
    ]

    by_trial = defaultdict(list)

    for record in selected:
        by_trial[record.trial].append(record)

    generations = []
    belief_rates = []
    repetition_rates = []
    exposed_counts = []
    confidences = []

    for trial in range(trials):
        records = by_trial[trial]

        generations.append(
            result.maximum_generation_by_trial[
                f"{condition}:{trial}"
            ]
        )
        belief_rates.append(
            sum(
                record.believes_claim
                for record in records
            )
            / len(records)
        )
        repetition_rates.append(
            sum(
                record.repeats_claim
                for record in records
            )
            / len(records)
        )
        exposed_counts.append(
            1 + len(records)
        )
        confidences.append(
            mean(
                record.belief_confidence
                for record in records
            )
        )

    return {
        "average_generation": mean(generations),
        "average_belief_rate": mean(belief_rates),
        "average_repetition_rate": mean(
            repetition_rates
        ),
        "average_exposed_agents": mean(
            exposed_counts
        ),
        "average_confidence": mean(confidences),
        "generations": generations,
    }


def main() -> None:
    trials_per_condition = 3

    config = ExperimentConfig(
        name="phase5-multi-claim-live-pilot",
        trials_per_condition=trials_per_condition,
        maximum_api_calls=18,
        maximum_cost_usd=0.10,
        estimated_output_tokens_per_call=180,
        dry_run=False,
    )
    config.validate_budget()

    total_planned_calls = (
        config.planned_api_calls
        * len(SEED_CLAIMS)
    )
    total_estimated_cost = (
        config.estimated_cost_usd
        * len(SEED_CLAIMS)
    )
    total_cost_ceiling = 0.15

    if total_estimated_cost > total_cost_ceiling:
        raise ValueError(
            "Combined estimated cost exceeds the pilot ceiling."
        )

    print("PHASE 5: LIVE MULTI-CLAIM PILOT")
    print("-" * 55)
    print(f"Claims: {len(SEED_CLAIMS)}")
    print(
        "Trials per condition per claim: "
        f"{trials_per_condition}"
    )
    print(
        "Maximum total API calls: "
        f"{total_planned_calls}"
    )
    print(
        "Worst-case estimated cost: "
        f"${total_estimated_cost:.4f}"
    )
    print(
        "Combined cost ceiling: "
        f"${total_cost_ceiling:.2f}"
    )
    print("-" * 55)

    decision_maker = OpenAIDecisionMaker(
        model=config.model,
    )

    saved_results = []
    summaries = {}

    for claim in SEED_CLAIMS:
        print(f"Running claim: {claim.id}")

        result = run_calibrated_pilot(
            config=config,
            decision_maker=decision_maker,
            original_message=claim.message,
        )

        baseline = summarize(
            result,
            "baseline",
            trials_per_condition,
        )
        skeptical = summarize(
            result,
            "skeptical",
            trials_per_condition,
        )

        summaries[claim.id] = {
            "baseline": baseline,
            "skeptical": skeptical,
        }

        saved_results.append(
            {
                "claim": asdict(claim),
                "calls_made": result.calls_made,
                "maximum_generation_by_trial": (
                    result.maximum_generation_by_trial
                ),
                "records": [
                    asdict(record)
                    for record in result.records
                ],
            }
        )

    output = Path(
        "results/phase5_multi_claim_live_pilot.json"
    )
    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output.write_text(
        json.dumps(
            {
                "model": config.model,
                "trials_per_condition": (
                    trials_per_condition
                ),
                "usage": asdict(
                    decision_maker.usage
                ),
                "observed_cost_usd": (
                    decision_maker
                    .usage
                    .estimated_cost_usd
                ),
                "summaries": summaries,
                "results": saved_results,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    print()
    print("MULTI-CLAIM PILOT RESULTS")
    print("-" * 55)

    for claim in SEED_CLAIMS:
        values = summaries[claim.id]
        baseline = values["baseline"]
        skeptical = values["skeptical"]

        print(claim.id)
        print(
            "  Baseline generation: "
            f"{baseline['average_generation']:.2f}"
        )
        print(
            "  Skeptical generation: "
            f"{skeptical['average_generation']:.2f}"
        )
        print(
            "  Baseline repetition: "
            f"{baseline['average_repetition_rate']:.3f}"
        )
        print(
            "  Skeptical repetition: "
            f"{skeptical['average_repetition_rate']:.3f}"
        )
        print(
            "  Baseline exposure: "
            f"{baseline['average_exposed_agents']:.2f}"
        )
        print(
            "  Skeptical exposure: "
            f"{skeptical['average_exposed_agents']:.2f}"
        )

    usage = decision_maker.usage

    print("-" * 55)
    print(f"Actual API calls: {usage.calls}")
    print(f"Input tokens: {usage.input_tokens}")
    print(f"Output tokens: {usage.output_tokens}")
    print(
        "Observed estimated cost: "
        f"${usage.estimated_cost_usd:.4f}"
    )
    print(f"Raw results saved to: {output}")
    print("-" * 55)
    print(
        "These are multi-claim pilot results, "
        "not final research conclusions."
    )


if __name__ == "__main__":
    main()
