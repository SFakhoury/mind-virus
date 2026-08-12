import unittest

from mind_virus.autonomous_town import AutonomousTown
from mind_virus.world import build_default_world


class AutonomousTownTests(unittest.TestCase):
    def setUp(self):
        self.world = build_default_world()
        self.world.absolute_minute = 510
        self.world.residents["Alice"].location_id = "town_hall"
        self.world.residents["Dana"].location_id = "town_hall"
        self.world.residents["Alice"].needs.social = 0.8
        self.town = AutonomousTown(world=self.world)

    def test_world_interaction_creates_grounded_conversation(self):
        memory = self.town.agents["Alice"].observe(
            "Dana discussed current town events at Town Hall.",
            6,
        )

        conversations = self.town.tick()

        self.assertEqual(len(conversations), 1)
        self.assertEqual(conversations[0].speaker, "Alice")
        self.assertEqual(conversations[0].listener, "Dana")
        self.assertIn(memory.id, conversations[0].supporting_memory_ids)
        self.assertEqual(
            conversations[0].topic_source_memory_ids,
            (memory.id,),
        )
        self.assertIn("selected a private memory", conversations[0].topic_reason)

    def test_conversation_is_stored_in_listener_memory(self):
        before = len(self.town.agents["Dana"].memories)

        self.town.tick()

        self.assertEqual(len(self.town.agents["Dana"].memories), before + 1)

    def test_conversation_is_stored_in_speaker_memory(self):
        before = len(self.town.agents["Alice"].memories)

        conversations = self.town.tick()

        self.assertEqual(len(self.town.agents["Alice"].memories), before + 1)
        self.assertEqual(
            self.town.agents["Alice"].memories.all()[-1].id,
            conversations[0].speaker_memory_id,
        )

    def test_interaction_event_is_processed_only_once(self):
        self.town.tick()
        first_count = len(self.town.conversations)

        self.town.process_new_interactions()

        self.assertEqual(len(self.town.conversations), first_count)

    def test_browser_state_contains_autonomous_conversations(self):
        self.town.tick()

        state = self.town.browser_state()

        self.assertEqual(len(state["autonomous_conversations"]), 1)
        self.assertEqual(
            state["autonomous_conversations"][0]["location_id"],
            "town_hall",
        )
        self.assertIn("autonomous_reflections", state)

    def test_requires_agent_for_every_world_resident(self):
        with self.assertRaises(ValueError):
            AutonomousTown(world=self.world, agents={})

    def test_default_town_produces_an_early_autonomous_conversation(self):
        town = AutonomousTown()

        town.tick(20)

        self.assertGreaterEqual(len(town.conversations), 1)
        self.assertEqual(town.conversations[0].speaker, "Dana")
        self.assertTrue(town.conversations[0].supporting_memory_ids)

    def test_conversation_automatically_triggers_ready_reflections(self):
        self.town.agents["Alice"].observe(
            "Current town events are discussed at Town Hall.",
            5,
        )
        self.town.agents["Alice"].observe(
            "Dana reviews current town events.",
            5,
        )
        self.town.agents["Dana"].observe(
            "Alice reports current town events.",
            5,
        )

        self.town.tick()

        reflected_agents = {item.agent for item in self.town.reflections}
        self.assertEqual(reflected_agents, {"Alice", "Dana"})
        for item in self.town.reflections:
            self.assertEqual(len(item.source_memory_ids), 3)

    def test_automatic_reflections_are_exposed_to_browser(self):
        for agent in self.town.agents.values():
            agent.observe("Current town events matter at Town Hall.", 5)
            agent.observe("Town Hall hosts discussion of current events.", 5)
        self.town.tick()

        state = self.town.browser_state()

        self.assertGreaterEqual(len(state["autonomous_reflections"]), 1)


if __name__ == "__main__":
    unittest.main()
