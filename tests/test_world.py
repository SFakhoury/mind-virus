import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from mind_virus.world import (
    Location,
    Needs,
    Route,
    WorldState,
    build_default_world,
    replay_default_world,
)


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

    def test_saved_world_loads_to_identical_state(self):
        world = build_default_world()
        world.tick(700)
        with TemporaryDirectory() as directory:
            checkpoint = world.save(Path(directory) / "world.json")
            restored = WorldState.load(checkpoint)

        self.assertEqual(restored.to_dict(), world.to_dict())

    def test_resumed_world_matches_uninterrupted_world(self):
        uninterrupted = build_default_world()
        uninterrupted.tick(1600)

        first_run = build_default_world()
        first_run.tick(800)
        with TemporaryDirectory() as directory:
            checkpoint = first_run.save(Path(directory) / "world.json")
            resumed = WorldState.load(checkpoint)
        resumed.tick(800)

        self.assertEqual(resumed.to_dict(), uninterrupted.to_dict())

    def test_replay_matches_original_world(self):
        original = build_default_world()
        original.tick(2880)
        replayed = replay_default_world(original.absolute_minute)

        self.assertEqual(replayed.to_dict(), original.to_dict())

    def test_replay_rejects_time_before_world_start(self):
        with self.assertRaises(ValueError):
            replay_default_world(479)

    def test_needs_reject_values_outside_unit_interval(self):
        with self.assertRaises(ValueError):
            Needs(energy=1.1)

    def test_needs_change_deterministically_with_time(self):
        world = build_default_world()
        initial = world.residents["Charlie"].needs
        initial_values = (initial.energy, initial.hunger, initial.social)
        world.tick(20)
        changed = world.residents["Charlie"].needs

        self.assertNotEqual(
            (changed.energy, changed.hunger, changed.social),
            initial_values,
        )
        self.assertGreater(changed.hunger, initial_values[1])
        self.assertGreater(changed.social, initial_values[2])

    def test_interaction_requires_shared_location(self):
        world = build_default_world()
        with self.assertRaises(ValueError):
            world.record_interaction("Alice", "Bob")

    def test_interaction_updates_both_relationships(self):
        world = build_default_world()
        world.residents["Alice"].location_id = "town_hall"
        world.residents["Dana"].location_id = "town_hall"
        world.residents["Alice"].needs.social = 0.8
        world.residents["Dana"].needs.social = 0.7

        world.record_interaction("Alice", "Dana")

        self.assertEqual(
            world.residents["Alice"].relationships["Dana"],
            0.52,
        )
        self.assertEqual(
            world.residents["Dana"].relationships["Alice"],
            0.52,
        )
        self.assertAlmostEqual(world.residents["Alice"].needs.social, 0.65)
        self.assertAlmostEqual(world.residents["Dana"].needs.social, 0.55)
        self.assertEqual(len(world.event_log), 1)

    def test_relationship_strength_is_clamped(self):
        world = build_default_world()
        alice = world.residents["Alice"]
        dana = world.residents["Dana"]
        alice.location_id = dana.location_id = "town_hall"
        alice.relationships["Dana"] = 0.99
        dana.relationships["Alice"] = 0.99

        world.record_interaction(
            "Alice",
            "Dana",
            relationship_delta=0.5,
        )

        self.assertEqual(alice.relationships["Dana"], 1.0)
        self.assertEqual(dana.relationships["Alice"], 1.0)

    def test_needs_and_relationships_survive_checkpoint(self):
        world = build_default_world()
        world.residents["Alice"].location_id = "town_hall"
        world.residents["Dana"].location_id = "town_hall"
        world.tick(10)
        world.record_interaction("Alice", "Dana")
        with TemporaryDirectory() as directory:
            checkpoint = world.save(Path(directory) / "world.json")
            restored = WorldState.load(checkpoint)

        self.assertEqual(restored.to_dict(), world.to_dict())

    def test_browser_state_contains_authoritative_clock_and_activity(self):
        world = build_default_world()
        state = world.browser_state()

        self.assertEqual(state["clock"], "DAY 01 · 08:00")
        self.assertEqual(state["residents"]["Alice"]["x"], 0.18)
        self.assertIn("activity", state["residents"]["Alice"])

    def test_travel_position_is_interpolated_by_python(self):
        world = build_default_world()
        world.tick(5)
        alice = world.browser_state()["residents"]["Alice"]

        self.assertEqual(alice["destination_id"], "town_hall")
        self.assertAlmostEqual(alice["x"], 0.18)
        self.assertAlmostEqual(alice["y"], 0.77)

    def test_browser_state_survives_checkpoint(self):
        world = build_default_world()
        world.tick(25)
        with TemporaryDirectory() as directory:
            checkpoint = world.save(Path(directory) / "world.json")
            restored = WorldState.load(checkpoint)

        self.assertEqual(restored.browser_state(), world.browser_state())

    def test_shortest_route_returns_next_connected_location(self):
        world = build_default_world()

        self.assertEqual(world.next_route_step("library", "bakery"), "town_hall")

    def test_hunger_decision_controls_activity_and_travel(self):
        world = build_default_world()
        alice = world.residents["Alice"]
        alice.location_id = "town_hall"
        alice.needs.hunger = 0.9

        world.tick()

        self.assertEqual(alice.activity, "eating")
        self.assertEqual(alice.decision_source, "hunger")
        self.assertEqual(alice.destination_id, "bakery")
        self.assertIn("hunger is high", alice.decision_reason)

    def test_indirect_autonomous_destination_uses_road_network(self):
        world = build_default_world()
        charlie = world.residents["Charlie"]
        charlie.location_id = "library"
        charlie.needs.hunger = 0.9

        world.tick()

        self.assertEqual(charlie.activity, "eating")
        self.assertEqual(charlie.destination_id, "town_hall")

    def test_browser_state_explains_resident_decision(self):
        world = build_default_world()
        world.tick()

        alice = world.browser_state()["residents"]["Alice"]
        self.assertEqual(alice["decision_source"], "schedule")
        self.assertIn("schedule", alice["decision_reason"])

    def test_daily_goal_memory_lineage_survives_checkpoint(self):
        world = build_default_world()
        alice = world.residents["Alice"]
        alice.daily_goal_day = 1
        alice.daily_goal = "investigate bakery report"
        alice.goal_destination_id = "bakery"
        alice.goal_activity = "investigating"
        alice.goal_source = "memory"
        alice.goal_memory_ids = ("memory-1",)
        with TemporaryDirectory() as directory:
            checkpoint = world.save(Path(directory) / "world.json")
            restored = WorldState.load(checkpoint)

        self.assertEqual(restored.to_dict(), world.to_dict())

    def test_socially_motivated_residents_interact_autonomously(self):
        world = build_default_world()
        world.absolute_minute = 510
        alice = world.residents["Alice"]
        dana = world.residents["Dana"]
        alice.location_id = dana.location_id = "town_hall"
        alice.needs.social = 0.8

        world.tick()

        self.assertEqual(alice.activity, "conversation")
        self.assertEqual(dana.activity, "conversation")
        self.assertEqual(alice.interaction_history[-1]["other"], "Dana")
        self.assertEqual(world.event_log[-1]["type"], "interaction")

    def test_autonomous_interaction_has_cooldown(self):
        world = build_default_world()
        world.absolute_minute = 510
        alice = world.residents["Alice"]
        dana = world.residents["Dana"]
        alice.location_id = dana.location_id = "town_hall"
        alice.needs.social = dana.needs.social = 1.0
        world.tick()
        first_count = len(alice.interaction_history)

        world.tick(11)

        self.assertEqual(len(alice.interaction_history), first_count)


if __name__ == "__main__":
    unittest.main()
