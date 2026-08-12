import unittest
from pathlib import Path

from scripts.run_town_ui import (
    HOST,
    PORT,
    UI_DIRECTORY,
    simulation_decision,
    usage_summary,
)
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

    def test_town_connects_to_python_api_and_uses_world_state(self):
        script = (UI_DIRECTORY / "town.js").read_text(encoding="utf-8")
        self.assertNotIn("elapsedHours", script)
        self.assertIn("clock.textContent=world.clock", script)
        self.assertIn('fetch("/api/state")', script)
        self.assertIn('fetch("/api/step"', script)
        self.assertIn('fetch("/api/chat"', script)
        self.assertIn('"/api/world/tick"', script)
        self.assertIn("p.x+=(p.tx-p.x)*.055", script)
        self.assertIn("p.y+=(p.ty-p.y)*.055", script)
        self.assertIn("resident.activity", script)
        self.assertIn("resident.decision_source", script)
        self.assertIn("resident.decision_reason", script)
        self.assertIn("resident.daily_goal", script)
        self.assertIn("Daily goal:", script)
        self.assertIn("world.autonomous_conversations", script)
        self.assertIn("listener_interpretation", script)
        self.assertIn("listener_believes", script)
        self.assertIn("listener_repeats", script)
        self.assertIn("seenAutonomousConversations", script)
        self.assertIn("seenAutonomousReflections", script)
        self.assertIn("world.autonomous_reflections", script)
        self.assertIn("source.bubbleUntil", script)
        self.assertIn('state.experience==="autonomous-town"', script)
        self.assertIn("!autonomousMode&&!sessionStopped", script)
        self.assertIn("LIVE AI MODE", script)
        self.assertIn('new EventSource("/api/v1/events")', script)
        self.assertNotIn("setInterval(refreshUsage", script)

    def test_server_exposes_versioned_persistence_routes(self):
        source = Path("scripts/run_town_ui.py").read_text(encoding="utf-8")
        self.assertIn('"/api/v1/health"', source)
        self.assertIn('"/api/v1/state"', source)
        self.assertIn('"/api/v1/state/latest"', source)
        self.assertIn("store.save_current_state", source)
        self.assertIn('"/api/v1/events"', source)
        self.assertIn("broker.publish", source)

    def test_autonomous_mode_hides_research_only_panels(self):
        markup = (UI_DIRECTORY / "index.html").read_text(encoding="utf-8")

        self.assertIn('id="research-claim"', markup)
        self.assertIn('id="research-metrics"', markup)

    def test_simulation_bob_uses_firsthand_evidence(self):
        alice = Agent("Alice", "Reporter")
        bob = Agent("Bob", "Bakery worker")
        decision = simulation_decision(bob, alice, "Bakery rumor")

        self.assertFalse(decision.believes_claim)
        self.assertFalse(decision.repeats_claim)
        self.assertIn("firsthand", decision.reason)

    def test_simulation_usage_is_zero(self):
        usage = usage_summary(simulation_decision, lambda *_: None)

        self.assertEqual(usage["calls"], 0)
        self.assertEqual(usage["input_tokens"], 0)
        self.assertEqual(usage["output_tokens"], 0)
        self.assertEqual(usage["estimated_cost_usd"], 0)


if __name__ == "__main__":
    unittest.main()
