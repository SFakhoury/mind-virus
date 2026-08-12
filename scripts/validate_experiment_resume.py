from pathlib import Path
import tempfile

from mind_virus.journal import ResultJournal


def main() -> None:
    print("PHASE 5: RESUMABLE EXPERIMENT VALIDATION")
    print("-" * 52)

    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "experiment.jsonl"
        journal = ResultJournal(path)

        journal.append(
            {
                "trial_key": "bakery:baseline:0",
                "claim_id": "bakery",
                "condition": "baseline",
                "trial": 0,
                "status": "complete",
            }
        )
        journal.append(
            {
                "trial_key": "bakery:skeptical:0",
                "claim_id": "bakery",
                "condition": "skeptical",
                "trial": 0,
                "status": "complete",
            }
        )

        resumed = ResultJournal(path)
        completed, expected = resumed.progress(120)

        print(f"Completed records restored: {completed}")
        print(f"Expected final records: {expected}")
        print(
            "Resume check: "
            f"{resumed.is_complete('bakery', 'baseline', 0)}"
        )

    print("-" * 52)
    print("No API requests were made.")
    print(
        "The final experiment can now resume "
        "without repeating saved trials."
    )


if __name__ == "__main__":
    main()
