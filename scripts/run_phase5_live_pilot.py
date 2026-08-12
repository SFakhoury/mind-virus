from collections import defaultdict
from statistics import mean

from mind_virus.ai_interpreter import OpenAIInterpreter
from mind_virus.analysis import (
    UNCERTAINTY_WORDS,
    similarity,
    word_set,
)
from mind_virus.config import ExperimentConfig
from mind_virus.pilot import (
    PilotRecord,
    run_pilot,
    save_pilot_result,
)


def summarize_condition(
    records: list[PilotRecord],
) -> dict[str, float]:
    """Summarize final mutation and uncertainty by condition."""
    by_trial: dict[int, list[PilotRecord]] = defaultdict(list)

    for record in records:
        by_trial[record.trial].append(record)

    final_similarities: list[float] = []
    uncertainty_counts: list[int] = []

    for trial_records in by_trial.values():
        ordered = sorted(
            trial_records,
            key=lambda record: record.generation,
        )

        original = ordered[0].input_message
        final = ordered[-1].interpreted_message

        final_similarities.append(
            similarity(original, final)
        )
        uncertainty_counts.append(
            len(word_set(final) & UNCERTAINTY_WORDS)
        )

    return {
        "average_final_similarity": mean(
            final_similarities
        ),
        "average_final_uncertainty": mean(
            uncertainty_counts
        ),
    }


def main() -> None:
    config = ExperimentConfig(
        name="phase5-live-pilot",
        dry_run=False,
    )
    config.validate_budget()

    print("PHASE 5: LIVE CONTROLLED AI PILOT")
    print("-" * 50)
    print(f"Model: {config.model}")
    print(
        "Trials: "
        f"{config.trials_per_condition} per condition"
    )
    print(f"Planned API calls: {config.planned_api_calls}")
    print(
        "Estimated cost: "
        f"${config.estimated_cost_usd:.4f}"
    )
    print(
        "Configured cost ceiling: "
        f"${config.maximum_cost_usd:.2f}"
    )
    print("-" * 50)

    interpreter = OpenAIInterpreter(
        model=config.model,
    )

    result = run_pilot(
        config=config,
        interpreter=interpreter,
    )

    output = save_pilot_result(
        result,
        "results/phase5_live_pilot.json",
    )

    baseline_records = [
        record
        for record in result.records
        if record.condition == "baseline"
    ]
    skeptical_records = [
        record
        for record in result.records
        if record.condition == "skeptical"
    ]

    baseline = summarize_condition(
        baseline_records
    )
    skeptical = summarize_condition(
        skeptical_records
    )

    print()
    print("PILOT RESULTS")
    print("-" * 50)
    print(
        "Baseline final similarity: "
        f"{baseline['average_final_similarity']:.3f}"
    )
    print(
        "Skeptical final similarity: "
        f"{skeptical['average_final_similarity']:.3f}"
    )
    print(
        "Baseline uncertainty signals: "
        f"{baseline['average_final_uncertainty']:.2f}"
    )
    print(
        "Skeptical uncertainty signals: "
        f"{skeptical['average_final_uncertainty']:.2f}"
    )
    print(f"Actual API calls: {result.api_calls}")
    print(f"Raw results saved to: {output}")
    print("-" * 50)
    print(
        "Pilot completed. These results are diagnostic, "
        "not final research evidence."
    )


if __name__ == "__main__":
    main()
