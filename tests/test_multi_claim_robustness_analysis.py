import unittest

from mind_virus.multi_claim_robustness_analysis import (
    analyze_multi_claim_robustness, render_multi_claim_report,
)


def item(claim, condition, believes, repeats):
    return {
        "claim_id": claim, "model": "model", "prompt_variant": "neutral",
        "condition": condition, "believes_claim": believes,
        "repeats_claim": repeats, "estimated_cost_usd": 0.001,
    }


class MultiClaimRobustnessAnalysisTests(unittest.TestCase):
    def setUp(self):
        self.records = [
            item("a", "baseline", True, True),
            item("a", "skeptical", False, False),
            item("b", "baseline", False, False),
            item("b", "skeptical", False, False),
        ]

    def test_reductions_and_floor_cells_are_separated(self):
        result = analyze_multi_claim_robustness(self.records)
        self.assertEqual(result.belief_reduction_cells, 1)
        self.assertEqual(result.repetition_reduction_cells, 1)
        self.assertEqual(result.belief_floor_cells, 1)
        self.assertEqual(result.repetition_floor_cells, 1)

    def test_no_change_at_floor_is_not_a_contradiction(self):
        result = analyze_multi_claim_robustness(self.records)
        self.assertEqual(result.contradictory_belief_cells, 0)
        self.assertEqual(result.contradictory_repetition_cells, 0)

    def test_cost_is_aggregated(self):
        self.assertAlmostEqual(
            analyze_multi_claim_robustness(self.records).estimated_cost_usd, 0.004
        )

    def test_unmatched_conditions_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "matched"):
            analyze_multi_claim_robustness(self.records[:-1])

    def test_report_preserves_diagnostic_limitation(self):
        report = render_multi_claim_report(
            analyze_multi_claim_robustness(self.records)
        )
        self.assertIn("not final confirmatory evidence", report)
        self.assertIn("floor effects", report)


if __name__ == "__main__":
    unittest.main()
