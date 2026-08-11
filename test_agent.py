import unittest

from agent import Agent


class AgentTests(unittest.TestCase):
    def test_agent_validates_name(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "name cannot be empty",
        ):
            Agent(
                name="   ",
                personality="Friendly and curious",
            )

    def test_agent_validates_personality(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "personality cannot be empty",
        ):
            Agent(
                name="Alice",
                personality="   ",
            )

    def test_remember_creates_and_stores_memory(self) -> None:
        alice = Agent(
            name="Alice",
            personality="Friendly and observant",
        )

        memory = alice.remember(
            content="The bakery was unusually crowded.",
            importance=6,
            source="observation",
        )

        self.assertEqual(len(alice.memories), 1)
        self.assertEqual(alice.memories.all(), [memory])
        self.assertEqual(
            memory.content,
            "The bakery was unusually crowded.",
        )
        self.assertEqual(memory.importance, 6)
        self.assertEqual(memory.source, "observation")

    def test_agents_have_private_memory_streams(self) -> None:
        alice = Agent(
            name="Alice",
            personality="Friendly and observant",
        )
        bob = Agent(
            name="Bob",
            personality="Reserved and analytical",
        )

        alice.remember(
            content="The bakery was crowded.",
            importance=6,
            source="observation",
        )

        self.assertEqual(len(alice.memories), 1)
        self.assertEqual(len(bob.memories), 0)
        self.assertIsNot(alice.memories, bob.memories)

    def test_recall_uses_memory_retrieval(self) -> None:
        alice = Agent(
            name="Alice",
            personality="Friendly and observant",
        )

        bakery_memory = alice.remember(
            content="The bakery was crowded this morning.",
            importance=8,
            source="observation",
        )
        alice.remember(
            content="The park was quiet in the afternoon.",
            importance=2,
            source="observation",
        )

        recalled = alice.recall(
            context="What happened at the bakery?",
            limit=1,
        )

        self.assertEqual(recalled, [bakery_memory])


if __name__ == "__main__":
    unittest.main()
