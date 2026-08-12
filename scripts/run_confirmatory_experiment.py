from __future__ import annotations

from mind_virus.confirmatory import (
    FINAL_EXPECTED_RECORDS,
    FINAL_MAXIMUM_API_CALLS,
    FINAL_MAXIMUM_COST_USD,
    journal_usage,
    next_pending_key,
    run_next_trial,
)
from mind_virus.decision import OpenAIDecisionMaker
from mind_virus.journal import ResultJournal


JOURNAL_PATH = (
    "results/phase5_confirmatory_experiment.jsonl"
)


def main() -> None:
    journal = ResultJournal(JOURNAL_PATH)
    usage = journal_usage(journal)

    completed, expected = journal.progress(
        FINAL_EXPECTED_RECORDS
    )

    print("PHASE 5: CONFIRMATORY DATA COLLECTION")
    print("-" * 58)
    print(f"Completed condition-trials: {completed}")
    print(f"Remaining condition-trials: {expected - completed}")
    print(
        "Maximum total model calls: "
        f"{FINAL_MAXIMUM_API_CALLS}"
    )
    print(
        "Previously completed calls: "
        f"{usage.calls}"
    )
    print(
        "Previously observed cost: "
        f"${usage.estimated_cost_usd:.4f}"
    )
    print(
        "Hard cost ceiling: "
        f"${FINAL_MAXIMUM_COST_USD:.2f}"
    )
    print(f"Checkpoint file: {JOURNAL_PATH}")
    print("-" * 58)

    if completed == expected:
        print("The confirmatory dataset is already complete.")
        return

    decision_maker = OpenAIDecisionMaker()

    try:
        while True:
            pending = next_pending_key(journal)

            if pending is None:
                break

            print(f"Running: {pending}")

            saved = run_next_trial(
                journal=journal,
                decision_maker=decision_maker,
                cumulative_usage=usage,
            )

            if saved is None:
                break

            completed, expected = journal.progress(
                FINAL_EXPECTED_RECORDS
            )

            print(
                f"  saved {completed}/{expected} | "
                f"generation={saved['maximum_generation']} | "
                f"exposed={saved['exposed_agents']} | "
                f"calls={usage.calls} | "
                f"cost=${usage.estimated_cost_usd:.4f}"
            )

    except KeyboardInterrupt:
        print()
        print("-" * 58)
        print("Collection stopped by the user.")
        print(
            f"Saved progress: "
            f"{len(journal.completed_keys())}/"
            f"{FINAL_EXPECTED_RECORDS}"
        )
        print(
            "Run the same command later to resume."
        )
        return

    except Exception:
        print()
        print("-" * 58)
        print(
            "Collection stopped after an error. "
            "Completed trials remain saved."
        )
        print(
            f"Saved progress: "
            f"{len(journal.completed_keys())}/"
            f"{FINAL_EXPECTED_RECORDS}"
        )
        print(
            "Fix the reported error, then run the same "
            "command to resume."
        )
        raise

    completed, expected = journal.progress(
        FINAL_EXPECTED_RECORDS
    )

    print()
    print("CONFIRMATORY COLLECTION COMPLETE")
    print("-" * 58)
    print(f"Saved condition-trials: {completed}/{expected}")
    print(f"Actual model calls: {usage.calls}")
    print(f"Input tokens: {usage.input_tokens}")
    print(f"Output tokens: {usage.output_tokens}")
    print(
        "Observed estimated cost: "
        f"${usage.estimated_cost_usd:.4f}"
    )
    print(f"Dataset saved to: {JOURNAL_PATH}")
    print("-" * 58)
    print(
        "The dataset is now ready for Phase 6 "
        "statistical analysis."
    )


if __name__ == "__main__":
    main()
