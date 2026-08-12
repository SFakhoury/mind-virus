from pathlib import Path
import tempfile
import unittest

from mind_virus.journal import ResultJournal


class JournalTests(unittest.TestCase):
    def test_trial_key_is_stable(self) -> None:
        key = ResultJournal.trial_key(
            "bakery",
            "skeptical",
            4,
        )

        self.assertEqual(
            key,
            "bakery:skeptical:4",
        )

    def test_completed_trial_is_restored(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            journal = ResultJournal(
                Path(directory) / "results.jsonl"
            )

            journal.append(
                {
                    "trial_key": (
                        "bakery:baseline:0"
                    ),
                    "claim_id": "bakery",
                    "condition": "baseline",
                    "trial": 0,
                }
            )

            restored = ResultJournal(
                journal.path
            )

            self.assertTrue(
                restored.is_complete(
                    "bakery",
                    "baseline",
                    0,
                )
            )
            self.assertEqual(
                restored.progress(10),
                (1, 10),
            )

    def test_duplicate_trial_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            journal = ResultJournal(
                Path(directory) / "results.jsonl"
            )
            record = {
                "trial_key": "bakery:baseline:0",
            }

            journal.append(record)

            with self.assertRaisesRegex(
                ValueError,
                "already recorded",
            ):
                journal.append(record)

    def test_invalid_condition_is_rejected(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "Condition must be",
        ):
            ResultJournal.trial_key(
                "bakery",
                "unknown",
                0,
            )

    def test_empty_journal_has_no_progress(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            journal = ResultJournal(
                Path(directory) / "missing.jsonl"
            )

            self.assertEqual(
                journal.records(),
                [],
            )
            self.assertEqual(
                journal.progress(120),
                (0, 120),
            )


if __name__ == "__main__":
    unittest.main()
