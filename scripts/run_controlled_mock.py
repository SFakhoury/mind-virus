from mind_virus.config import ExperimentConfig
from mind_virus.controlled_pilot import (
    run_controlled_pilot,
    save_controlled_result,
)
from mind_virus.decision import TransmissionDecision


def mock_decision(listener, speaker, message):
    skeptical = "Skeptical" in listener.personality

    return TransmissionDecision(
        remembered_message=(
            f"{speaker.name} passed along an unconfirmed "
            "claim about free bread."
        ),
        believes_claim=not skeptical,
        repeats_claim=not skeptical,
        belief_confidence=0.2 if skeptical else 0.7,
        reason=(
            "The claim lacks evidence."
            if skeptical
            else "I generally trust social reports."
        ),
    )


def main() -> None:
    config = ExperimentConfig()
    result = run_controlled_pilot(
        config,
        mock_decision,
    )

    output = save_controlled_result(
        result,
        "results/phase5_controlled_mock.json",
    )

    baseline = [
        generation
        for key, generation
        in result.maximum_generation_by_trial.items()
        if key.startswith("baseline:")
    ]
    skeptical = [
        generation
        for key, generation
        in result.maximum_generation_by_trial.items()
        if key.startswith("skeptical:")
    ]

    print("PHASE 5: CONTROLLED DECISION MOCK")
    print("-" * 48)
    print(
        "Baseline generations: "
        f"{baseline}"
    )
    print(
        "Skeptical generations: "
        f"{skeptical}"
    )
    print(f"Calls needed: {result.calls_made}")
    print(f"Results saved to: {output}")
    print("-" * 48)
    print("No API requests were made.")
    print("Belief and repetition are now measured separately.")


if __name__ == "__main__":
    main()
