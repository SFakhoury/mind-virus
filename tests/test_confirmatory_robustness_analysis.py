import unittest

from mind_virus.confirmatory_robustness_analysis import analyze_confirmatory_robustness


def records() -> list[dict[str, object]]:
    output = []
    for claim in ("a", "b", "c"):
        for model in ("m1", "m2"):
            for prompt in ("p1", "p2"):
                for condition in ("baseline", "skeptical"):
                    for trial in range(27):
                        output.append({"claim_id": claim, "model": model, "prompt_variant": prompt,
                            "condition": condition, "trial": trial, "repeats_claim": condition == "baseline",
                            "believes_claim": condition == "baseline" and trial < 9, "estimated_cost_usd": 0.001})
    return output


class ConfirmatoryRobustnessAnalysisTests(unittest.TestCase):
    def test_analyzes_complete_matched_design(self):
        result = analyze_confirmatory_robustness(records())
        self.assertEqual((result.records, result.cells), (648, 12))
        self.assertEqual(result.primary.difference, -1.0)
        self.assertAlmostEqual(result.secondary.difference, -1 / 3)
        self.assertLess(result.primary.exact_p_value, 0.05)

    def test_incomplete_dataset_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "exactly 648"):
            analyze_confirmatory_robustness(records()[:-1])

    def test_cost_is_aggregated(self):
        self.assertAlmostEqual(analyze_confirmatory_robustness(records()).estimated_cost_usd, 0.648)


if __name__ == "__main__":
    unittest.main()
