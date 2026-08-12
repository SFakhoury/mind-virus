import unittest

from mind_virus.live_robustness_analysis import (
    analyze_live_robustness, render_live_pilot_report,
)


def record(model, prompt, condition, trial, believes, repeats):
    return {
        "model": model, "prompt_variant": prompt, "condition": condition,
        "trial": trial, "believes_claim": believes, "repeats_claim": repeats,
        "input_tokens": 10, "output_tokens": 5, "estimated_cost_usd": 0.001,
    }


class LiveRobustnessAnalysisTests(unittest.TestCase):
    def setUp(self):
        self.records = [
            record("a", "neutral", "baseline", 0, True, True),
            record("a", "neutral", "baseline", 1, False, True),
            record("a", "neutral", "skeptical", 0, False, False),
            record("a", "neutral", "skeptical", 1, False, False),
        ]

    def test_cell_effects_are_skeptical_minus_baseline(self):
        cell = analyze_live_robustness(self.records).cells[0]
        self.assertEqual(cell.belief_difference, -0.5)
        self.assertEqual(cell.repetition_difference, -1.0)

    def test_direction_consistency_is_reported(self):
        analysis = analyze_live_robustness(self.records)
        self.assertEqual(analysis.belief_direction_consistency, 1.0)
        self.assertEqual(analysis.repetition_direction_consistency, 1.0)

    def test_usage_is_aggregated(self):
        analysis = analyze_live_robustness(self.records)
        self.assertEqual(analysis.total_input_tokens, 40)
        self.assertEqual(analysis.total_output_tokens, 20)
        self.assertAlmostEqual(analysis.estimated_cost_usd, 0.004)

    def test_unmatched_conditions_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "matched"):
            analyze_live_robustness(self.records[:-1])

    def test_report_states_diagnostic_limitations(self):
        report = render_live_pilot_report(analyze_live_robustness(self.records))
        self.assertIn("not a final confirmatory dataset", report)
        self.assertIn("floor effect", report)


if __name__ == "__main__":
    unittest.main()
