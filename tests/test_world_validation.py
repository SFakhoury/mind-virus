import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from mind_virus.world import WorldEvent, build_default_world
from mind_virus.world_validation import save_validation, validate_world


class WorldValidationTests(unittest.TestCase):
    def test_world_event_validates_importance(self):
        with self.assertRaises(ValueError):
            WorldEvent("event", 500, "library", "Description", 11)

    def test_scheduled_events_trigger_once(self):
        world = build_default_world()
        world.tick(200)
        events = [
            event for event in world.event_log
            if event["type"] == "world_event"
        ]

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["event_id"], "day1_bus_inspection")
        self.assertEqual(world.triggered_event_ids, {"day1_bus_inspection"})

    def test_three_day_validation_passes(self):
        _, report = validate_world(days=3)

        self.assertTrue(report.passed)
        self.assertEqual(report.scheduled_events_triggered, 3)
        self.assertTrue(report.replay_identical)

    def test_validation_rejects_zero_days(self):
        with self.assertRaises(ValueError):
            validate_world(days=0)

    def test_validation_report_is_saved(self):
        world, report = validate_world(days=1)
        with TemporaryDirectory() as directory:
            output = save_validation(
                world,
                report,
                Path(directory) / "validation.json",
            )
            saved = json.loads(output.read_text(encoding="utf-8"))

        self.assertEqual(saved["report"]["simulated_days"], 1)
        self.assertEqual(saved["passed"], report.passed)


if __name__ == "__main__":
    unittest.main()
