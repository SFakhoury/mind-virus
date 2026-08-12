from mind_virus.confirmatory import (
    FINAL_EXPECTED_RECORDS,
    FINAL_MAXIMUM_API_CALLS,
    FINAL_MAXIMUM_COST_USD,
    planned_trial_keys,
)
from mind_virus.seed_claims import SEED_CLAIMS


def main() -> None:
    observed_cost_per_call = 0.0491 / 53
    projected_cost = (
        FINAL_MAXIMUM_API_CALLS
        * observed_cost_per_call
    )

    print("PHASE 5: FINAL EXPERIMENT PREVIEW")
    print("-" * 52)
    print(f"Claims: {len(SEED_CLAIMS)}")
    print("Trials per condition per claim: 20")
    print(f"Condition-trials: {FINAL_EXPECTED_RECORDS}")
    print(
        "Maximum model calls: "
        f"{FINAL_MAXIMUM_API_CALLS}"
    )
    print(
        "Projected cost from pilot usage: "
        f"${projected_cost:.2f}"
    )
    print(
        "Hard experiment cost ceiling: "
        f"${FINAL_MAXIMUM_COST_USD:.2f}"
    )
    print(
        "Unique planned trial keys: "
        f"{len(set(planned_trial_keys()))}"
    )
    print("-" * 52)
    print("Checkpoint interval: after every condition-trial")
    print("Resume support: enabled")
    print("No API requests were made.")
    print("The final runner is ready for confirmatory collection.")


if __name__ == "__main__":
    main()
