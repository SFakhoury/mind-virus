import unittest

from mind_virus.world_runtime import WorldClock


class WorldClockTests(unittest.TestCase):
    def test_tick_once_uses_single_server_callback(self):
        ticks = []
        clock = WorldClock(lambda: ticks.append("tick"), interval_seconds=1)

        clock.tick_once()

        self.assertEqual(ticks, ["tick"])

    def test_interval_must_be_positive(self):
        with self.assertRaises(ValueError):
            WorldClock(lambda: None, interval_seconds=0)


if __name__ == "__main__":
    unittest.main()
