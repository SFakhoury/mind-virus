import json
from pathlib import Path
import tempfile
import unittest

from mind_virus.analysis import (
    analyze_chain,
    load_and_analyze,
    similarity,
)


class AnalysisTests(unittest.TestCase):
    def test_identical_messages_have_full_similarity(self) -> None:
        self.assertEqual(
            similarity(
                "The bakery has free bread.",
                "The bakery has free bread.",
            ),
            1.0,
        )

    def test_different_messages_have_lower_similarity(self) -> None:
        score = similarity(
            "The bakery has free bread.",
            "The park was quiet.",
        )

        self.assertLess(score, 0.5)

    def test_chain_analysis_measures_mutation(self) -> None:
        transcript = [
            {
                "generation": 0,
                "message": "The bakery has free bread.",
            },
            {
                "generation": 1,
                "message": (
                    "Alice claimed the bakery might have free bread."
                ),
            },
            {
                "generation": 2,
                "message": (
                    "Bob heard an unconfirmed bakery rumor."
                ),
            },
        ]

        metrics = analyze_chain(transcript)

        self.assertEqual(metrics.generations, 2)
        self.assertLess(metrics.original_similarity, 1.0)
        self.assertGreater(metrics.average_step_similarity, 0.0)
        self.assertGreaterEqual(metrics.uncertainty_mentions, 3)

    def test_saved_transcript_can_be_analyzed(self) -> None:
        transcript = [
            {"generation": 0, "message": "Original message"},
            {"generation": 1, "message": "Changed message"},
        ]

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "chain.json"
            path.write_text(
                json.dumps(transcript),
                encoding="utf-8",
            )

            metrics = load_and_analyze(path)

        self.assertEqual(metrics.generations, 1)


if __name__ == "__main__":
    unittest.main()
