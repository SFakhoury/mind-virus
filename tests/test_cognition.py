import unittest

from mind_virus.cognition import choose_resident_action
from mind_virus.world import build_default_world


class CognitionTests(unittest.TestCase):
    def setUp(self):
        self.world = build_default_world()
        self.alice = self.world.residents["Alice"]

    def test_normal_resident_follows_schedule(self):
        decision = choose_resident_action(self.alice, 480)

        self.assertEqual(decision.source, "schedule")
        self.assertEqual(decision.activity, "reporting")
        self.assertEqual(decision.destination_id, "town_hall")

    def test_low_energy_overrides_schedule(self):
        self.alice.needs.energy = 0.20

        decision = choose_resident_action(self.alice, 480)

        self.assertEqual(decision.source, "energy")
        self.assertEqual(decision.activity, "resting")
        self.assertEqual(decision.destination_id, "alice_home")

    def test_high_hunger_selects_bakery(self):
        self.alice.needs.hunger = 0.80

        decision = choose_resident_action(self.alice, 480)

        self.assertEqual(decision.source, "hunger")
        self.assertEqual(decision.activity, "eating")
        self.assertEqual(decision.destination_id, "bakery")

    def test_high_social_need_selects_town_hall(self):
        self.alice.needs.social = 0.80

        decision = choose_resident_action(self.alice, 1020)

        self.assertEqual(decision.source, "social")
        self.assertEqual(decision.activity, "socializing")
        self.assertEqual(decision.destination_id, "town_hall")

    def test_most_urgent_need_wins(self):
        self.alice.needs.energy = 0.20
        self.alice.needs.hunger = 0.90

        decision = choose_resident_action(self.alice, 480)

        self.assertEqual(decision.source, "hunger")
        self.assertAlmostEqual(decision.urgency, 0.90)

    def test_decision_does_not_mutate_resident(self):
        before = self.alice.location_id, self.alice.activity

        choose_resident_action(self.alice, 480)

        self.assertEqual((self.alice.location_id, self.alice.activity), before)

    def test_rejects_invalid_minute(self):
        with self.assertRaises(ValueError):
            choose_resident_action(self.alice, 1440)


if __name__ == "__main__":
    unittest.main()
