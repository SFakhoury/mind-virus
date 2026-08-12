from collections import defaultdict
from statistics import mean

from mind_virus.assignment import assign_agents
from mind_virus.calibrated_pilot import (
    run_calibrated_pilot,
)
from mind_virus.config import ExperimentConfig
from mind_virus.controlled_pilot import (
    ControlledRecord,
    save_controlled_result,
)
from mind_virus.decision import OpenAIDecisionMaker


def summarize(
    records: tuple[ControlledRecord, ...],
    maximum_generations: dict[str, int],
    condition: str,
    trials: int,
) -> dict[str, float]:
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

    belief_rates = []
    repetition_rates = []
    exposure_counts = []
    confidences = []
    generations = []

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
        exposure_counts.append(
            1 + len(trial_records)
        )
        confidences.append(
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
        "belief_rate": mean(belief_rates),
        "repetition_rate": mean(repetition_rates),
        "exposed_agents": mean(exposure_counts),
        "confidence": mean(confidences),
        "maximum_generation": mean(generations),
    }


def print_summary(
    title: str,
    values: dict[str, float],
) -> None:
    print(title)
    print(
        f"  Belief rate: {values['belief_rate']:.3f}"
    )
    print(
        "  Repetition rate: "
        f"{values['repetition_rate']:.3f}"
    )
    print(
        "  Exposed agents: "
        f"{values['exposed_agents']:.2f}"
    )
    print(
        f"  Confidence: {values['confidence']:.3f}"
    )
    print(
        "  Maximum generation: "
        f"{values['maximum_generation']:.2f}"
    )


def main() -> None:
    config = ExperimentConfig(
        name="phase5-calibrated-live-pilot",
        estimated_output_tokens_per_call=180,
        dry_run=False,
    )
    config.validate_budget()

    print("PHASE 5: CALIBRATED LIVE AI PILOT")
    print("-" * 52)
    print(f"Model: {config.model}")
    print(
        f"Trials: {config.trials_per_condition} "
        "per condition"
    )
    print(
        "Skeptic fraction: "
        f"{config.skeptic_fraction:.0%}"
    )
    print(
        "Maximum API calls: "
        f"{config.maximum_api_calls}"
    )
    print(
        "Worst-case estimated cost: "
        f"${config.estimated_cost_usd:.4f}"
    )
    print("-" * 52)

    for trial in range(
        config.trials_per_condition
    ):
        _, positions = assign_agents(
            condition="skeptical",
            count=config.agents_per_trial,
            skeptic_fraction=config.skeptic_fraction,
            seed=config.seed + trial,
        )

        print(
            f"Trial {trial} skeptic positions: "
            f"{sorted(positions)}"
        )

    print("-" * 52)

    result = run_calibrated_pilot(
        config=config,
        decision_maker=OpenAIDecisionMaker(
            model=config.model,
        ),
    )

    output = save_controlled_result(
        result,
        "results/phase5_calibrated_live_pilot.json",
    )

    baseline = summarize(
        result.records,
        result.maximum_generation_by_trial,
        "baseline",
        config.trials_per_condition,
    )
    skeptical = summarize(
        result.records,
        result.maximum_generation_by_trial,
        "skeptical",
        config.trials_per_condition,
    )

    print()
    print("CALIBRATED PILOT RESULTS")
    print("-" * 52)
    print_summary("Baseline:", baseline)
    print_summary("Skeptical society:", skeptical)

    print()
    print("PER-TRIAL MAXIMUM GENERATION")
    print("-" * 52)

    for trial in range(
        config.trials_per_condition
    ):
        baseline_generation = (
            result.maximum_generation_by_trial[
                f"baseline:{trial}"
            ]
        )
        skeptical_generation = (
            result.maximum_generation_by_trial[
                f"skeptical:{trial}"
            ]
        )

        print(
            f"Trial {trial}: "
            f"baseline={baseline_generation}, "
            f"skeptical={skeptical_generation}"
        )

    print("-" * 52)
    print(f"Actual API calls: {result.calls_made}")
    print(f"Raw decisions saved to: {output}")
    print(
        "These remain pilot results and are not "
        "final research conclusions."
    )


if __name__ == "__main__":
    main()
