from pathlib import Path
import tempfile
import unittest

from mind_virus.config import ExperimentConfig


class ExperimentConfigTests(unittest.TestCase):
    def test_planned_calls_are_calculated(self) -> None:
        config = ExperimentConfig(
            trials_per_condition=5,
            agents_per_trial=4,
        )

        self.assertEqual(config.planned_api_calls, 30)

    def test_luna_cost_is_estimated(self) -> None:
        config = ExperimentConfig(
            trials_per_condition=5,
            agents_per_trial=4,
            estimated_input_tokens_per_call=500,
            estimated_output_tokens_per_call=80,
        )

        expected = (
            30 * 500 / 1_000_000 * 1.00
            + 30 * 80 / 1_000_000 * 6.00
        )

        self.assertAlmostEqual(
            config.estimated_cost_usd,
            expected,
        )

    def test_call_limit_is_enforced(self) -> None:
        config = ExperimentConfig(
            trials_per_condition=10,
            maximum_api_calls=30,
        )

        with self.assertRaisesRegex(
            ValueError,
            "API calls exceed",
        ):
            config.validate_budget()

    def test_cost_limit_is_enforced(self) -> None:
        config = ExperimentConfig(
            maximum_cost_usd=0.001,
        )

        with self.assertRaisesRegex(
            ValueError,
            "cost exceeds",
        ):
            config.validate_budget()

    def test_configuration_can_be_saved(self) -> None:
        config = ExperimentConfig()

        with tempfile.TemporaryDirectory() as directory:
            path = config.save(
                Path(directory) / "config.json"
            )

            contents = path.read_text(encoding="utf-8")

        self.assertIn('"dry_run": true', contents)
        self.assertIn('"planned_api_calls": 30', contents)


if __name__ == "__main__":
    unittest.main()
