from collections import defaultdict
from statistics import mean

from mind_virus.config import ExperimentConfig
from mind_virus.controlled_pilot import (
    ControlledRecord,
    run_controlled_pilot,
    save_controlled_result,
)
from mind_virus.decision import OpenAIDecisionMaker


def summarize(
    records: tuple[ControlledRecord, ...],
    maximum_generations: dict[str, int],
    condition: str,
    trials: int,
) -> dict[str, float]:
    """Calculate pilot outcomes for one condition."""
    selected = [
        record
        for record in records
        if record.condition == condition
    ]

    by_trial: dict[int, list[ControlledRecord]] = defaultdict(
        list
    )

    for record in selected:
        by_trial[record.trial].append(record)

    belief_rates: list[float] = []
    repetition_rates: list[float] = []
    exposed_counts: list[int] = []
    average_confidences: list[float] = []
    generations: list[int] = []

    for trial in range(trials):
        trial_records = by_trial[trial]

        belief_rates.append(
            sum(
                record.believes_claim
                for record in trial_records
            )
            / len(trial_records)
        )
        repetition_rates.append(
            sum(
                record.repeats_claim
                for record in trial_records
            )
            / len(trial_records)
        )
        exposed_counts.append(
            1 + len(trial_records)
        )
        average_confidences.append(
            mean(
                record.belief_confidence
                for record in trial_records
            )
        )
        generations.append(
            maximum_generations[
                f"{condition}:{trial}"
            ]
        )

    return {
        "average_belief_rate": mean(belief_rates),
        "average_repetition_rate": mean(
            repetition_rates
        ),
        "average_exposed_agents": mean(exposed_counts),
        "average_confidence": mean(
            average_confidences
        ),
        "average_max_generation": mean(generations),
    }


def print_summary(
    label: str,
    summary: dict[str, float],
) -> None:
    print(label)
    print(
        "  Belief rate: "
        f"{summary['average_belief_rate']:.3f}"
    )
    print(
        "  Repetition rate: "
        f"{summary['average_repetition_rate']:.3f}"
    )
    print(
        "  Exposed agents: "
        f"{summary['average_exposed_agents']:.2f}"
    )
    print(
        "  Belief confidence: "
        f"{summary['average_confidence']:.3f}"
    )
    print(
        "  Maximum generation: "
        f"{summary['average_max_generation']:.2f}"
    )


def main() -> None:
    config = ExperimentConfig(
        name="phase5-corrected-live-pilot",
        estimated_output_tokens_per_call=180,
        dry_run=False,
    )
    config.validate_budget()

    print("PHASE 5: CORRECTED CONTROLLED AI PILOT")
    print("-" * 52)
    print(f"Model: {config.model}")
    print(
        "Trials: "
        f"{config.trials_per_condition} per condition"
    )
    print(
        "Maximum API calls: "
        f"{config.maximum_api_calls}"
    )
    print(
        "Worst-case estimated cost: "
        f"${config.estimated_cost_usd:.4f}"
    )
    print(
        "Configured cost ceiling: "
        f"${config.maximum_cost_usd:.2f}"
    )
    print("-" * 52)

    decision_maker = OpenAIDecisionMaker(
        model=config.model,
    )

    result = run_controlled_pilot(
        config=config,
        decision_maker=decision_maker,
    )

    output = save_controlled_result(
        result,
        "results/phase5_corrected_live_pilot.json",
    )

    baseline = summarize(
        records=result.records,
        maximum_generations=(
            result.maximum_generation_by_trial
        ),
        condition="baseline",
        trials=config.trials_per_condition,
    )
    skeptical = summarize(
        records=result.records,
        maximum_generations=(
            result.maximum_generation_by_trial
        ),
        condition="skeptical",
        trials=config.trials_per_condition,
    )

    print()
    print("CORRECTED PILOT RESULTS")
    print("-" * 52)
    print_summary("Baseline:", baseline)
    print_summary("Skeptical:", skeptical)
    print()
    print(f"Actual API calls: {result.calls_made}")
    print(f"Raw decisions saved to: {output}")
    print("-" * 52)
    print(
        "These are diagnostic pilot results, "
        "not final research conclusions."
    )


if __name__ == "__main__":
    main()
