import csv
from pathlib import Path
import tempfile
import unittest

from mind_virus.experiment import (
    run_comparison,
    run_trial,
    summarize,
    write_results,
)


class ExperimentTests(unittest.TestCase):
    def test_trial_is_reproducible(self) -> None:
        first = run_trial(
            condition="skeptical",
            trial=0,
            seed=1234,
            skeptic_fraction=0.35,
        )
        second = run_trial(
            condition="skeptical",
            trial=0,
            seed=1234,
            skeptic_fraction=0.35,
        )

        self.assertEqual(first, second)

    def test_comparison_creates_matched_trials(self) -> None:
        results = run_comparison(
            trials=10,
            seed=100,
        )

        baseline = [
            result
            for result in results
            if result.condition == "baseline"
        ]
        skeptical = [
            result
            for result in results
            if result.condition == "skeptical"
        ]

        self.assertEqual(len(baseline), 10)
        self.assertEqual(len(skeptical), 10)

        self.assertEqual(
            [result.trial for result in baseline],
            [result.trial for result in skeptical],
        )

    def test_skepticism_does_not_increase_propagation(
        self,
    ) -> None:
        results = run_comparison(
            trials=100,
            seed=500,
            skeptic_fraction=0.35,
        )
        summary = summarize(results)

        self.assertLessEqual(
            summary["skeptical"]["average_believers"],
            summary["baseline"]["average_believers"],
        )
        self.assertLessEqual(
            summary["skeptical"]["average_max_generation"],
            summary["baseline"]["average_max_generation"],
        )

    def test_results_can_be_written_to_csv(self) -> None:
        results = run_comparison(
            trials=3,
            seed=900,
        )

        with tempfile.TemporaryDirectory() as directory:
            output = write_results(
                results,
                Path(directory) / "results.csv",
            )

            self.assertTrue(output.exists())

            with output.open(
                encoding="utf-8",
                newline="",
            ) as input_file:
                rows = list(csv.DictReader(input_file))

            self.assertEqual(len(rows), 6)
            self.assertEqual(
                set(rows[0]),
                {
                    "condition",
                    "trial",
                    "exposed_agents",
                    "believing_agents",
                    "belief_rate",
                    "max_generation",
                    "total_agents",
                },
            )

    def test_trial_arguments_are_validated(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "Condition must be",
        ):
            run_trial(
                condition="unknown",
                trial=0,
                seed=1,
            )

        with self.assertRaisesRegex(
            ValueError,
            "Agent count must be",
        ):
            run_trial(
                condition="baseline",
                trial=0,
                seed=1,
                agent_count=1,
            )


if __name__ == "__main__":
    unittest.main()

