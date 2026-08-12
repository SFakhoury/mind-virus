import unittest

from mind_virus.agent import Agent
from mind_virus.autonomous_interpretation import interpret_autonomous_message


class AutonomousInterpretationTests(unittest.TestCase):
    def setUp(self):
        self.alice = Agent("Alice", "A sociable reporter")
        self.bob = Agent("Bob", "A skeptical and evidence-seeking baker")

    def test_interpretation_attributes_message_to_speaker(self):
        result = interpret_autonomous_message(
            self.bob,
            self.alice,
            "Town Hall opens at nine.",
        )

        self.assertTrue(result.remembered_message.startswith("Alice shared:"))

    def test_unsupported_message_is_remembered_but_not_believed(self):
        result = interpret_autonomous_message(
            self.bob,
            self.alice,
            "The bakery has a surprise event.",
        )

        self.assertFalse(result.believes_message)
        self.assertFalse(result.repeats_message)

    def test_grounded_message_can_be_believed_by_normal_listener(self):
        dana = Agent("Dana", "A town planner")

        result = interpret_autonomous_message(
            dana,
            self.alice,
            "Town Hall hosts public planning.",
            supporting_memory_ids=("source-1",),
            relationship_trust=0.8,
        )

        self.assertTrue(result.believes_message)
        self.assertTrue(result.repeats_message)

    def test_skeptic_uses_higher_acceptance_threshold(self):
        result = interpret_autonomous_message(
            self.bob,
            self.alice,
            "Town Hall hosts public planning.",
            supporting_memory_ids=("source-1",),
        )

        self.assertEqual(result.acceptance_threshold, 0.7)
        self.assertFalse(result.believes_message)

    def test_contradictory_memory_reduces_confidence(self):
        self.bob.observe("No surprise bakery event was announced.", 9)

        result = interpret_autonomous_message(
            self.bob,
            self.alice,
            "The bakery has a surprise event.",
            supporting_memory_ids=("source-1",),
            relationship_trust=1.0,
        )

        self.assertFalse(result.believes_message)
        self.assertFalse(result.repeats_message)
        self.assertIn("contradicts", result.reason)

    def test_relationship_trust_is_validated(self):
        with self.assertRaises(ValueError):
            interpret_autonomous_message(
                self.bob,
                self.alice,
                "Message",
                relationship_trust=1.1,
            )


if __name__ == "__main__":
    unittest.main()
