from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock
import unittest

from mind_virus.decision import TransmissionDecision
from mind_virus.live_robustness_pilot import (
    LiveRobustnessPlan, collect_live_robustness_pilot,
)


class Usage:
    input_tokens = 100
    output_tokens = 20


class LiveRobustnessPilotTests(unittest.TestCase):
    def setUp(self):
        self.client = Mock()
        self.client.responses.parse.return_value = Mock(
            output_parsed=TransmissionDecision(
                remembered_message="Alice reported an unsupported bakery claim.",
                believes_claim=False, repeats_claim=False,
                belief_confidence=0.2, reason="No direct evidence.",
            ),
            usage=Usage(),
        )

    def test_default_plan_has_bounded_calls_and_cost(self):
        plan = LiveRobustnessPlan()
        self.assertEqual(plan.planned_calls, 32)
        self.assertLess(plan.estimated_cost_usd, plan.cost_ceiling_usd)

    def test_fake_collection_completes_every_cell(self):
        with TemporaryDirectory() as directory:
            records = collect_live_robustness_pilot(
                LiveRobustnessPlan(), Path(directory) / "results.json",
                client=self.client,
            )
        self.assertEqual(len(records), 32)
        self.assertEqual(self.client.responses.parse.call_count, 32)

    def test_checkpoint_resume_skips_completed_calls(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "results.json"
            first = collect_live_robustness_pilot(
                LiveRobustnessPlan(), path, client=self.client
            )
            calls = self.client.responses.parse.call_count
            second = collect_live_robustness_pilot(
                LiveRobustnessPlan(), path, client=self.client
            )
        self.assertEqual(first, second)
        self.assertEqual(self.client.responses.parse.call_count, calls)

    def test_unknown_model_without_pricing_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "pricing"):
            LiveRobustnessPlan(models=("unknown",)).validate()

    def test_too_low_cost_ceiling_is_rejected_before_calls(self):
        plan = LiveRobustnessPlan(cost_ceiling_usd=0.001)
        with TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "hard ceiling"):
                collect_live_robustness_pilot(
                    plan, Path(directory) / "results.json", client=self.client
                )
        self.client.responses.parse.assert_not_called()


if __name__ == "__main__":
    unittest.main()
