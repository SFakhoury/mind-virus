import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from mind_virus.world import Location, Route, build_default_world


class WorldTests(unittest.TestCase):
    def test_location_rejects_invalid_coordinates(self):
        with self.assertRaises(ValueError):
            Location("bad", "Bad", 1.1, 0.5)

    def test_route_rejects_zero_travel_time(self):
        with self.assertRaises(ValueError):
            Route("a", "b", 0)

    def test_clock_advances_across_day_boundary(self):
        world = build_default_world()
        world.absolute_minute = 1439
        world.tick()

        self.assertEqual(world.day, 2)
        self.assertEqual(world.minute_of_day, 0)

    def test_schedule_starts_real_travel(self):
        world = build_default_world()
        world.tick()
        alice = world.residents["Alice"]

        self.assertEqual(alice.destination_id, "town_hall")
        self.assertEqual(alice.travel_remaining, 8)
        self.assertEqual(world.event_log[-1]["type"], "departure")

    def test_resident_arrives_after_route_travel_time(self):
        world = build_default_world()
        world.tick(9)
        alice = world.residents["Alice"]

        self.assertEqual(alice.location_id, "town_hall")
        self.assertIsNone(alice.destination_id)
        self.assertEqual(alice.travel_remaining, 0)

    def test_world_snapshot_is_serializable(self):
        world = build_default_world()
        world.tick(15)
        with TemporaryDirectory() as directory:
            output = world.save(Path(directory) / "world.json")
            saved = json.loads(output.read_text(encoding="utf-8"))

        self.assertEqual(saved["absolute_minute"], 495)
        self.assertIn("Alice", saved["residents"])
        self.assertGreater(len(saved["event_log"]), 0)


if __name__ == "__main__":
    unittest.main()
