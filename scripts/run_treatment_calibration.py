from mind_virus.assignment import assign_agents
from mind_virus.calibrated_pilot import (
    run_calibrated_pilot,
)
from mind_virus.config import ExperimentConfig
from mind_virus.decision import TransmissionDecision


def mock_decision(listener, speaker, message):
    skeptical = (
        "corroborating evidence"
        in listener.personality
    )

    return TransmissionDecision(
        remembered_message=(
            f"{speaker.name} shared an unconfirmed "
            "bakery claim."
        ),
        believes_claim=not skeptical,
        repeats_claim=not skeptical,
        belief_confidence=0.2 if skeptical else 0.6,
        reason=(
            "No corroboration is available."
            if skeptical
            else "The report seems plausible."
        ),
    )


def main() -> None:
    config = ExperimentConfig()
    result = run_calibrated_pilot(
        config,
        mock_decision,
    )

    print("PHASE 5: TREATMENT CALIBRATION")
    print("-" * 50)

    for trial in range(
        config.trials_per_condition
    ):
        _, positions = assign_agents(
            condition="skeptical",
            count=config.agents_per_trial,
            skeptic_fraction=config.skeptic_fraction,
            seed=config.seed + trial,
        )

        generation = (
            result.maximum_generation_by_trial[
                f"skeptical:{trial}"
            ]
        )

        print(
            f"Trial {trial}: "
            f"skeptics={sorted(positions)}, "
            f"maximum_generation={generation}"
        )

    print("-" * 50)
    print(f"Mock calls made: {result.calls_made}")
    print("No API requests were made.")
    print("Treatment assignment is calibrated and reproducible.")


if __name__ == "__main__":
    main()
