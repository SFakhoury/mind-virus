import unittest
from pathlib import Path

from scripts.run_town_ui import HOST, PORT, UI_DIRECTORY, simulation_decision
from mind_virus.agent import Agent


class TownUIServerTests(unittest.TestCase):
    def test_server_uses_local_address(self):
        self.assertEqual(HOST, "127.0.0.1")
        self.assertEqual(PORT, 8000)

    def test_ui_directory_is_town_ui(self):
        self.assertEqual(UI_DIRECTORY.name, "town_ui")
        self.assertIsInstance(UI_DIRECTORY, Path)

    def test_ui_assets_exist(self):
        self.assertTrue((UI_DIRECTORY / "index.html").is_file())
        self.assertTrue((UI_DIRECTORY / "styles.css").is_file())
        self.assertTrue((UI_DIRECTORY / "town.js").is_file())

    def test_town_supports_continuing_conversations_and_days(self):
        script = (UI_DIRECTORY / "town.js").read_text(encoding="utf-8")
        self.assertIn("followUps", script)
        self.assertIn("elapsedHours", script)
        self.assertIn("DAY ${String(day)", script)
        self.assertIn("let target=people.find", script)
        self.assertIn("I work there, and no giveaway was announced", script)

    def test_simulation_bob_uses_firsthand_evidence(self):
        alice = Agent("Alice", "Reporter")
        bob = Agent("Bob", "Bakery worker")
        decision = simulation_decision(bob, alice, "Bakery rumor")

        self.assertFalse(decision.believes_claim)
        self.assertFalse(decision.repeats_claim)
        self.assertIn("firsthand", decision.reason)


if __name__ == "__main__":
    unittest.main()
