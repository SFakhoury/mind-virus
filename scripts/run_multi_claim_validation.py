from mind_virus.calibrated_pilot import (
    run_calibrated_pilot,
)
from mind_virus.config import ExperimentConfig
from mind_virus.decision import TransmissionDecision
from mind_virus.seed_claims import SEED_CLAIMS


def mock_decision(listener, speaker, message):
    skeptical = (
        "corroborating evidence"
        in listener.personality
    )

    return TransmissionDecision(
        remembered_message=(
            f"{speaker.name} shared an unverified report "
            f"about this topic: {message}"
        ),
        believes_claim=not skeptical,
        repeats_claim=not skeptical,
        belief_confidence=0.2 if skeptical else 0.6,
        reason=(
            "The report lacks corroboration."
            if skeptical
            else "The report is interesting enough to discuss."
        ),
    )


def main() -> None:
    config = ExperimentConfig(
        trials_per_condition=1,
        agents_per_trial=4,
        maximum_api_calls=6,
    )

    print("PHASE 5: MULTI-CLAIM VALIDATION")
    print("-" * 52)

    for claim in SEED_CLAIMS:
        result = run_calibrated_pilot(
            config=config,
            decision_maker=mock_decision,
            original_message=claim.message,
        )

        baseline = (
            result.maximum_generation_by_trial[
                "baseline:0"
            ]
        )
        skeptical = (
            result.maximum_generation_by_trial[
                "skeptical:0"
            ]
        )

        print(f"Claim: {claim.id}")
        print(
            f"  Baseline generation: {baseline}"
        )
        print(
            f"  Skeptical generation: {skeptical}"
        )

    print("-" * 52)
    print("No API requests were made.")
    print("All seed claims passed through the experiment runner.")


if __name__ == "__main__":
    main()
