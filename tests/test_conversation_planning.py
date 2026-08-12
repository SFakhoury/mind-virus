import unittest

from mind_virus.agent import Agent
from mind_virus.conversation_planning import plan_grounded_conversation
from mind_virus.memory_context import ConversationContext


class ConversationPlanningTests(unittest.TestCase):
    def setUp(self):
        self.alice = Agent("Alice", "Reporter")
        self.bob = Agent("Bob", "Baker")
        self.context = ConversationContext(
            "Bob",
            "Sunrise Bakery",
            "conversation",
            "free bread",
        )

    def test_plan_records_retrieved_memory_lineage(self):
        memory = self.alice.observe(
            "Bob said no free-bread giveaway was announced at Sunrise Bakery.",
            8,
        )

        plan = plan_grounded_conversation(
            self.alice,
            self.bob,
            self.context,
        )

        self.assertEqual(plan.memory_ids, (memory.id,))
        self.assertIn(memory.content, plan.grounding)
        self.assertIn(memory.content, plan.proposed_message)

    def test_plan_exposes_situation_and_query(self):
        plan = plan_grounded_conversation(
            self.alice,
            self.bob,
            self.context,
        )

        self.assertEqual(plan.speaker_name, "Alice")
        self.assertEqual(plan.listener_name, "Bob")
        self.assertEqual(plan.location_name, "Sunrise Bakery")
        self.assertIn("Bob", plan.retrieval_query)
        self.assertEqual(plan.topic, "free bread")

    def test_plan_without_memory_does_not_invent_facts(self):
        plan = plan_grounded_conversation(
            self.alice,
            self.bob,
            self.context,
        )

        self.assertFalse(plan.has_memory_support)
        self.assertIn("do not have a relevant memory", plan.proposed_message)
        self.assertIn("cannot make a factual claim", plan.proposed_message)

    def test_context_partner_must_match_listener(self):
        wrong_context = ConversationContext(
            "Dana",
            "Town Hall",
            "planning",
        )

        with self.assertRaises(ValueError):
            plan_grounded_conversation(
                self.alice,
                self.bob,
                wrong_context,
            )

    def test_plan_respects_memory_limit(self):
        for number in range(4):
            self.alice.observe(f"Bob bakery memory {number}", 5)

        plan = plan_grounded_conversation(
            self.alice,
            self.bob,
            self.context,
            memory_limit=2,
        )

        self.assertEqual(len(plan.memory_ids), 2)


if __name__ == "__main__":
    unittest.main()
