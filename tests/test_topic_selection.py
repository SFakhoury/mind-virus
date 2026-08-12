import unittest

from mind_virus.agent import Agent
from mind_virus.topic_selection import select_conversation_topic


class TopicSelectionTests(unittest.TestCase):
    def setUp(self):
        self.dana = Agent("Dana", "Planner")

    def test_selects_memory_relevant_to_current_location(self):
        memory = self.dana.observe(
            "At Town Hall, I review public plans and current town events.",
            5,
        )

        topic = select_conversation_topic(
            self.dana,
            partner_name="Alice",
            location_name="Town Hall",
            activity="conversation",
        )

        self.assertTrue(topic.memory_grounded)
        self.assertEqual(topic.source_memory_ids, (memory.id,))
        self.assertIn("Town Hall", topic.label)

    def test_unrelated_memory_does_not_become_topic(self):
        self.dana.observe("The bakery displayed normal bread prices.", 10)

        topic = select_conversation_topic(
            self.dana,
            partner_name="Alice",
            location_name="Town Hall",
            activity="planning",
        )

        self.assertFalse(topic.memory_grounded)
        self.assertEqual(topic.label, "planning at Town Hall")

    def test_partner_memory_can_determine_topic(self):
        memory = self.dana.remember(
            "Alice asked about the morning report.",
            5,
            "dialogue",
        )

        topic = select_conversation_topic(
            self.dana,
            partner_name="Alice",
            location_name="Town Hall",
            activity="conversation",
        )

        self.assertEqual(topic.source_memory_ids, (memory.id,))

    def test_topic_reason_is_auditable(self):
        self.dana.observe("Alice visited Town Hall.", 5)

        topic = select_conversation_topic(
            self.dana,
            partner_name="Alice",
            location_name="Town Hall",
            activity="conversation",
        )

        self.assertIn("selected a private memory", topic.reason)

    def test_topic_selection_validates_context(self):
        with self.assertRaises(ValueError):
            select_conversation_topic(
                self.dana,
                partner_name="",
                location_name="Town Hall",
                activity="conversation",
            )


if __name__ == "__main__":
    unittest.main()
