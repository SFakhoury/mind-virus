from pathlib import Path
import tempfile
import unittest

from mind_virus.confirmatory import (
    FINAL_EXPECTED_RECORDS,
    FINAL_MAXIMUM_API_CALLS,
    journal_usage,
    next_pending_key,
    planned_trial_keys,
    run_next_trial,
)
from mind_virus.decision import (
    ModelUsage,
    TransmissionDecision,
)
from mind_virus.journal import ResultJournal


class FakeDecisionMaker:
    def __init__(self) -> None:
        self.usage = ModelUsage()

    def __call__(
        self,
        listener,
        speaker,
        message,
    ) -> TransmissionDecision:
        skeptical = (
            "corroborating evidence"
            in listener.personality
        )

        self.usage.calls += 1
        self.usage.input_tokens += 300
        self.usage.output_tokens += 100

        return TransmissionDecision(
            remembered_message=(
                f"{speaker.name} shared the claim."
            ),
            believes_claim=not skeptical,
            repeats_claim=not skeptical,
            belief_confidence=(
                0.2 if skeptical else 0.5
            ),
            reason=(
                "No corroboration."
                if skeptical
                else "Worth discussing."
            ),
        )


class ConfirmatoryTests(unittest.TestCase):
    def test_final_plan_contains_120_records(
        self,
    ) -> None:
        keys = planned_trial_keys()

        self.assertEqual(
            len(keys),
            FINAL_EXPECTED_RECORDS,
        )
        self.assertEqual(
            len(keys),
            len(set(keys)),
        )
        self.assertEqual(
            FINAL_MAXIMUM_API_CALLS,
            360,
        )

    def test_next_trial_skips_saved_record(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            journal = ResultJournal(
                Path(directory) / "final.jsonl"
            )
            first = planned_trial_keys()[0]

            journal.append(
                {
                    "trial_key": first,
                    "usage": {
                        "calls": 1,
                        "input_tokens": 10,
                        "output_tokens": 5,
                    },
                }
            )

            self.assertEqual(
                next_pending_key(journal),
                planned_trial_keys()[1],
            )

    def test_one_trial_is_saved_with_usage(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            journal = ResultJournal(
                Path(directory) / "final.jsonl"
            )
            usage = ModelUsage()

            saved = run_next_trial(
                journal,
                FakeDecisionMaker(),
                cumulative_usage=usage,
            )

            self.assertIsNotNone(saved)
            self.assertEqual(
                len(journal.records()),
                1,
            )
            self.assertGreater(
                saved["usage"]["calls"],
                0,
            )
            self.assertGreater(
                saved["observed_cost_usd"],
                0,
            )

    def test_saved_usage_is_restored(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            journal = ResultJournal(
                Path(directory) / "final.jsonl"
            )

            journal.append(
                {
                    "trial_key": (
                        "bakery_free_bread:baseline:0"
                    ),
                    "usage": {
                        "calls": 3,
                        "input_tokens": 900,
                        "output_tokens": 300,
                    },
                }
            )

            usage = journal_usage(journal)

            self.assertEqual(usage.calls, 3)
            self.assertEqual(
                usage.input_tokens,
                900,
            )
            self.assertEqual(
                usage.output_tokens,
                300,
            )


if __name__ == "__main__":
    unittest.main()
