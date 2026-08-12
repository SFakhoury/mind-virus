import unittest

from mind_virus.robust_statistics import (
    adjust_benjamini_hochberg, analyze_paired_effect,
)


class RobustStatisticsTests(unittest.TestCase):
    def test_paired_effect_reports_raw_and_standardized_change(self):
        result = analyze_paired_effect(
            [1.0, 2.0, 3.0, 4.0], [0.5, 1.0, 2.5, 2.0],
            bootstrap_iterations=1000,
        )
        self.assertLess(result.mean_difference, 0)
        self.assertLess(result.standardized_effect_dz, 0)
        self.assertEqual(result.sample_size, 4)

    def test_constant_paired_differences_have_undefined_standardization(self):
        result = analyze_paired_effect(
            [2.0, 3.0, 4.0], [1.0, 2.0, 3.0], bootstrap_iterations=1000
        )
        self.assertIsNone(result.standardized_effect_dz)
        self.assertEqual(result.mean_difference, -1.0)

    def test_single_pair_has_no_standardized_effect(self):
        result = analyze_paired_effect(
            [1.0], [0.0], bootstrap_iterations=100
        )
        self.assertIsNone(result.standardized_effect_dz)

    def test_bh_adjustment_preserves_input_outcome_order(self):
        results = adjust_benjamini_hochberg(
            {"belief": 0.01, "exposure": 0.20, "repetition": 0.03}
        )
        self.assertEqual(
            [item.outcome for item in results], ["belief", "exposure", "repetition"]
        )

    def test_bh_adjusted_values_are_known(self):
        results = adjust_benjamini_hochberg({"a": 0.01, "b": 0.04, "c": 0.03})
        values = {item.outcome: item.adjusted_p_value for item in results}
        self.assertAlmostEqual(values["a"], 0.03)
        self.assertAlmostEqual(values["b"], 0.04)
        self.assertAlmostEqual(values["c"], 0.04)

    def test_rejection_uses_adjusted_not_raw_value(self):
        result = adjust_benjamini_hochberg({"a": 0.04, "b": 0.50})[0]
        self.assertFalse(result.rejected)
        self.assertGreater(result.adjusted_p_value, result.raw_p_value)

    def test_invalid_p_value_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "between 0 and 1"):
            adjust_benjamini_hochberg({"belief": 1.2})

    def test_empty_comparison_family_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "At least one"):
            adjust_benjamini_hochberg({})


if __name__ == "__main__":
    unittest.main()
