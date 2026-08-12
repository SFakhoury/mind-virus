from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from mind_virus.robustness_analysis import (
    RobustnessObservation, summarize_robustness,
)


def observation(cell, effect, low, high):
    return RobustnessObservation(cell, "belief_rate", effect, low, high)


class RobustnessAnalysisTests(unittest.TestCase):
    def test_consistent_supported_effect_survives(self):
        summary = summarize_robustness([
            observation("a", -0.20, -0.30, -0.10),
            observation("b", -0.10, -0.20, -0.01),
            observation("c", -0.05, -0.15, 0.05),
        ], expected_direction="lower", minimum_consistency=0.66)
        self.assertTrue(summary.conclusion_survives)
        self.assertEqual(summary.significant_supporting_cells, 2)
        self.assertEqual(summary.inconclusive_cells, 1)

    def test_significant_contradiction_blocks_conclusion(self):
        summary = summarize_robustness([
            observation("a", -0.20, -0.30, -0.10),
            observation("b", 0.20, 0.10, 0.30),
        ], expected_direction="lower", minimum_consistency=0.5)
        self.assertFalse(summary.conclusion_survives)
        self.assertEqual(summary.significant_contradicting_cells, 1)

    def test_direction_threshold_is_enforced(self):
        summary = summarize_robustness([
            observation("a", -0.20, -0.30, -0.10),
            observation("b", -0.05, -0.15, 0.05),
            observation("c", 0.01, -0.10, 0.10),
        ], expected_direction="lower", minimum_consistency=0.8)
        self.assertFalse(summary.conclusion_survives)
        self.assertAlmostEqual(summary.direction_consistency, 2 / 3)

    def test_null_cells_are_preserved_as_inconclusive(self):
        summary = summarize_robustness([
            observation("a", 0.0, -0.1, 0.1),
            observation("b", 0.0, 0.0, 0.0),
        ], expected_direction="lower")
        self.assertEqual(summary.inconclusive_cells, 2)
        self.assertFalse(summary.conclusion_survives)

    def test_mixed_outcomes_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "one outcome"):
            summarize_robustness([
                observation("a", -0.1, -0.2, 0.0),
                RobustnessObservation("b", "exposure", -1.0, -2.0, 0.0),
            ], expected_direction="lower")

    def test_duplicate_cells_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "unique"):
            summarize_robustness([
                observation("a", -0.1, -0.2, 0.0),
                observation("a", -0.2, -0.3, -0.1),
            ], expected_direction="lower")

    def test_effect_must_be_inside_interval(self):
        with self.assertRaisesRegex(ValueError, "inside"):
            observation("a", -0.5, -0.2, 0.0)

    def test_summary_can_be_saved_as_reproducible_artifact(self):
        summary = summarize_robustness([
            observation("a", -0.2, -0.3, -0.1)
        ], expected_direction="lower")
        with TemporaryDirectory() as directory:
            path = summary.save(Path(directory) / "summary.json")
            payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertTrue(payload["conclusion_survives"])
        self.assertEqual(payload["outcome"], "belief_rate")


if __name__ == "__main__":
    unittest.main()
