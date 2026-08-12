import unittest

from mind_virus.agent import Agent
from mind_virus.planning import create_daily_plan
from mind_virus.world import build_default_world


class DailyPlanningTests(unittest.TestCase):
    def setUp(self):
        self.world = build_default_world()
        self.alice = self.world.residents["Alice"]
        self.agent = Agent("Alice", "A careful local reporter.")

    def test_role_produces_default_daily_goal(self):
        plan = create_daily_plan(
            self.agent, self.alice, self.world.locations, 1
        )

        self.assertEqual(plan.source, "role")
        self.assertEqual(plan.destination_id, "town_hall")
        self.assertEqual(plan.activity, "reporting")

    def test_location_memory_changes_daily_goal(self):
        memory = self.agent.observe(
            "I should investigate a report at Sunrise Bakery.", 7
        )

        plan = create_daily_plan(
            self.agent, self.alice, self.world.locations, 1
        )

        self.assertEqual(plan.source, "memory")
        self.assertEqual(plan.destination_id, "bakery")
        self.assertEqual(plan.activity, "investigating")
        self.assertEqual(plan.source_memory_ids, (memory.id,))

    def test_critical_energy_overrides_role_and_memory(self):
        self.agent.observe("Visit Sunrise Bakery.", 8)
        self.alice.needs.energy = 0.2

        plan = create_daily_plan(
            self.agent, self.alice, self.world.locations, 1
        )

        self.assertEqual(plan.source, "energy")
        self.assertEqual(plan.destination_id, "alice_home")

    def test_high_hunger_creates_meal_goal(self):
        self.alice.needs.hunger = 0.8

        plan = create_daily_plan(
            self.agent, self.alice, self.world.locations, 1
        )

        self.assertEqual(plan.source, "hunger")
        self.assertEqual(plan.activity, "eating")

    def test_plan_validates_day(self):
        with self.assertRaises(ValueError):
            create_daily_plan(
                self.agent, self.alice, self.world.locations, 0
            )


if __name__ == "__main__":
    unittest.main()
