from pathlib import Path
import tempfile
import unittest

from mind_virus.config import ExperimentConfig
from mind_virus.pilot import (
    build_agents,
    run_pilot,
    save_pilot_result,
)


def fake_interpreter(listener, speaker, message):
    if "Skeptical" in listener.personality:
        return (
            f"{speaker.name} repeated an unconfirmed report "
            "about possible free bread."
        )

    return (
        f"{speaker.name} said the bakery is giving away "
        "free bread."
    )


class PilotTests(unittest.TestCase):
    def test_conditions_change_skepticism_only(self) -> None:
        baseline = build_agents("baseline", 4)
        skeptical = build_agents("skeptical", 4)

        self.assertEqual(
            [agent.name for agent in baseline],
            [agent.name for agent in skeptical],
        )
        self.assertNotEqual(
            baseline[1].personality,
            skeptical[1].personality,
        )

    def test_pilot_uses_planned_number_of_calls(self) -> None:
        config = ExperimentConfig()

        result = run_pilot(
            config=config,
            interpreter=fake_interpreter,
        )

        self.assertEqual(
            result.api_calls,
            config.planned_api_calls,
        )
        self.assertEqual(
            len(result.records),
            config.planned_api_calls,
        )

    def test_trials_are_matched_across_conditions(self) -> None:
        config = ExperimentConfig(
            trials_per_condition=2,
            maximum_api_calls=12,
        )

        result = run_pilot(
            config=config,
            interpreter=fake_interpreter,
        )

        first_messages = {
            (record.trial, record.condition):
                record.input_message
            for record in result.records
            if record.generation == 1
        }

        for trial in range(2):
            self.assertEqual(
                first_messages[(trial, "baseline")],
                first_messages[(trial, "skeptical")],
            )

    def test_dry_run_uses_injected_interpreter(self) -> None:
        calls = []

        def tracked_interpreter(listener, speaker, message):
            calls.append((listener.name, speaker.name))
            return "Locally generated test interpretation."

        config = ExperimentConfig(
            trials_per_condition=1,
            agents_per_trial=3,
            maximum_api_calls=4,
        )

        result = run_pilot(
            config=config,
            interpreter=tracked_interpreter,
        )

        self.assertTrue(result.dry_run)
        self.assertEqual(len(calls), 4)
        self.assertEqual(result.api_calls, 4)

    def test_pilot_results_can_be_saved(self) -> None:
        config = ExperimentConfig(
            trials_per_condition=1,
            agents_per_trial=2,
            maximum_api_calls=2,
        )

        result = run_pilot(
            config=config,
            interpreter=fake_interpreter,
        )

        with tempfile.TemporaryDirectory() as directory:
            output = save_pilot_result(
                result,
                Path(directory) / "pilot.json",
            )
            contents = output.read_text(
                encoding="utf-8"
            )

        self.assertIn('"dry_run": true', contents)
        self.assertIn('"baseline"', contents)
        self.assertIn('"skeptical"', contents)


if __name__ == "__main__":
    unittest.main()
