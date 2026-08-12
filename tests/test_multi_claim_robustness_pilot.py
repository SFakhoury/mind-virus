from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock
import unittest

from mind_virus.decision import TransmissionDecision
from mind_virus.multi_claim_robustness_pilot import (
    MultiClaimRobustnessPlan, collect_multi_claim_robustness,
)


class Usage:
    input_tokens = 100
    output_tokens = 20


class MultiClaimRobustnessPilotTests(unittest.TestCase):
    def setUp(self):
        self.client = Mock()
        self.client.responses.parse.return_value = Mock(
            output_parsed=TransmissionDecision(
                remembered_message="Alice reported an unsupported claim.",
                believes_claim=False, repeats_claim=False,
                belief_confidence=0.2, reason="No direct evidence.",
            ), usage=Usage(),
        )

    def test_default_plan_has_three_claims_and_bounded_cost(self):
        plan = MultiClaimRobustnessPlan()
        self.assertEqual(plan.planned_calls, 96)
        self.assertEqual(plan.base.estimated_output_tokens, 200)
        self.assertLess(plan.estimated_cost_usd, plan.cost_ceiling_usd)

    def test_collection_covers_every_claim_and_cell(self):
        with TemporaryDirectory() as directory:
            records = collect_multi_claim_robustness(
                MultiClaimRobustnessPlan(), Path(directory) / "data.json",
                client=self.client,
            )
        self.assertEqual(len(records), 96)
        self.assertEqual(len({item["claim_id"] for item in records}), 3)

    def test_collection_resumes_without_duplicate_calls(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "data.json"
            collect_multi_claim_robustness(
                MultiClaimRobustnessPlan(), path, client=self.client
            )
            calls = self.client.responses.parse.call_count
            collect_multi_claim_robustness(
                MultiClaimRobustnessPlan(), path, client=self.client
            )
        self.assertEqual(self.client.responses.parse.call_count, calls)

    def test_duplicate_claim_ids_are_rejected(self):
        plan = MultiClaimRobustnessPlan(claims=(("same", "one"), ("same", "two")))
        with self.assertRaisesRegex(ValueError, "unique"):
            plan.validate()


if __name__ == "__main__":
    unittest.main()
