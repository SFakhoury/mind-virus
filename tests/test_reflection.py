import unittest

from mind_virus.agent import Agent
from mind_virus.reflection import reflect_on_memories


class ReflectionTests(unittest.TestCase):
    def setUp(self):
        self.alice = Agent("Alice", "Reporter")

    def add_bakery_memories(self):
        return [
            self.alice.observe("The bakery displayed normal prices today.", 6),
            self.alice.hear(
                Agent("Bob", "Baker"),
                "The bakery announced no giveaway.",
                7,
            ),
            self.alice.observe("The bakery operated normally this morning.", 5),
        ]

    def test_reflection_requires_enough_memories(self):
        self.alice.observe("The bakery was open.", 5)

        self.assertIsNone(reflect_on_memories(self.alice, "bakery"))

    def test_reflection_is_stored_as_private_memory(self):
        self.add_bakery_memories()

        reflection = reflect_on_memories(self.alice, "bakery")

        self.assertEqual(reflection.source, "reflection")
        self.assertIn(reflection, self.alice.memories.all())

    def test_reflection_preserves_source_memory_lineage(self):
        sources = self.add_bakery_memories()

        reflection = reflect_on_memories(self.alice, "bakery")

        self.assertEqual(
            set(reflection.related_memory_ids),
            {memory.id for memory in sources},
        )

    def test_reflection_identifies_recurring_details(self):
        self.add_bakery_memories()

        reflection = reflect_on_memories(self.alice, "bakery")

        self.assertIn("recurring details", reflection.content)
        self.assertIn("bakery", reflection.content)

    def test_same_evidence_does_not_create_duplicate_reflection(self):
        self.add_bakery_memories()
        first = reflect_on_memories(self.alice, "bakery")

        second = reflect_on_memories(self.alice, "bakery")

        self.assertIs(second, first)
        self.assertEqual(
            len([m for m in self.alice.memories.all() if m.source == "reflection"]),
            1,
        )

    def test_reflection_validates_arguments(self):
        with self.assertRaises(ValueError):
            reflect_on_memories(self.alice, "")
        with self.assertRaises(ValueError):
            reflect_on_memories(
                self.alice,
                "bakery",
                minimum_memories=3,
                limit=2,
            )


if __name__ == "__main__":
    unittest.main()
