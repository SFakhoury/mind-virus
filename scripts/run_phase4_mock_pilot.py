from collections import Counter

from mind_virus.config import ExperimentConfig
from mind_virus.pilot import (
    run_pilot,
    save_pilot_result,
)


def mock_interpreter(listener, speaker, message):
    """Local stand-in used to validate experiment mechanics."""
    if "Skeptical" in listener.personality:
        return (
            f"{speaker.name} passed along an unconfirmed report "
            "that the bakery might have free bread."
        )

    return (
        f"{speaker.name} said the bakery is giving away "
        "free bread."
    )


def main() -> None:
    config = ExperimentConfig()
    config.validate_budget()

    result = run_pilot(
        config=config,
        interpreter=mock_interpreter,
    )

    output = save_pilot_result(
        result,
        "results/phase4_mock_pilot.json",
    )

    condition_counts = Counter(
        record.condition
        for record in result.records
    )

    print("PHASE 4: MOCK PILOT VALIDATION")
    print("-" * 48)
    print(
        "Baseline transmissions: "
        f"{condition_counts['baseline']}"
    )
    print(
        "Skeptical transmissions: "
        f"{condition_counts['skeptical']}"
    )
    print(f"Total interpretations: {result.api_calls}")
    print(f"Dry run: {result.dry_run}")
    print(f"Results saved to: {output}")
    print("-" * 48)
    print("No OpenAI API requests were made.")
    print("Phase 4 pilot machinery is ready.")


if __name__ == "__main__":
    main()
