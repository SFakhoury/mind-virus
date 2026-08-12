import unittest

from mind_virus.agent import Agent
from mind_virus.memory_context import (
    ConversationContext,
    retrieve_conversation_context,
)


class MemoryContextTests(unittest.TestCase):
    def setUp(self):
        self.alice = Agent("Alice", "Reporter")

    def test_query_contains_person_place_activity_and_topic(self):
        context = ConversationContext(
            partner_name="Bob",
            location_name="Sunrise Bakery",
            activity="reporting",
            topic="free bread",
        )

        self.assertEqual(
            context.retrieval_query,
            "Bob Sunrise Bakery reporting free bread",
        )

    def test_context_rejects_missing_grounding(self):
        with self.assertRaises(ValueError):
            ConversationContext("", "Bakery", "reporting")

    def test_retrieval_prefers_contextually_matching_memory(self):
        relevant = self.alice.remember(
            "Bob discussed free bread at Sunrise Bakery while I was reporting.",
            5,
            "dialogue",
        )
        self.alice.remember(
            "Dana discussed bus schedules at Town Hall.",
            5,
            "dialogue",
        )
        context = ConversationContext(
            "Bob",
            "Sunrise Bakery",
            "reporting",
            "free bread",
        )

        retrieved = retrieve_conversation_context(self.alice, context, limit=1)

        self.assertEqual(retrieved.memories, (relevant,))

    def test_retrieval_exposes_auditable_query(self):
        self.alice.observe("Bob arrived at the bakery.", 4)
        context = ConversationContext("Bob", "Bakery", "conversation")

        retrieved = retrieve_conversation_context(self.alice, context)

        self.assertEqual(retrieved.query, context.retrieval_query)

    def test_retrieval_respects_limit(self):
        for number in range(3):
            self.alice.observe(f"Bob bakery observation {number}", 5)
        context = ConversationContext("Bob", "Bakery", "conversation")

        retrieved = retrieve_conversation_context(
            self.alice,
            context,
            limit=2,
        )

        self.assertEqual(len(retrieved.memories), 2)


if __name__ == "__main__":
    unittest.main()
