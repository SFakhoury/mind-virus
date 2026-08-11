import unittest

from agent import Agent


class AgentInteractionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.alice = Agent(
            name="Alice",
            personality="Friendly, curious, and observant",
        )
        self.bob = Agent(
            name="Bob",
            personality="Reserved, careful, and analytical",
        )

    def test_observe_creates_observation_memory(self) -> None:
        memory = self.alice.observe(
            event="The bakery was unusually crowded.",
            importance=6,
        )

        self.assertEqual(memory.source, "observation")
        self.assertEqual(
            memory.content,
            "The bakery was unusually crowded.",
        )
        self.assertEqual(self.alice.memories.all(), [memory])

    def test_hear_creates_dialogue_memory(self) -> None:
        memory = self.bob.hear(
            speaker=self.alice,
            message="The bakery was unusually crowded.",
            importance=7,
        )

        self.assertEqual(memory.source, "dialogue")
        self.assertEqual(
            memory.content,
            'Alice said: "The bakery was unusually crowded."',
        )

    def test_heard_memory_is_private_to_listener(self) -> None:
        self.bob.hear(
            speaker=self.alice,
            message="The bakery was unusually crowded.",
            importance=7,
        )

        self.assertEqual(len(self.bob.memories), 1)
        self.assertEqual(len(self.alice.memories), 0)

    def test_hear_rejects_empty_message(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "Dialogue message cannot be empty",
        ):
            self.bob.hear(
                speaker=self.alice,
                message="   ",
                importance=5,
            )


if __name__ == "__main__":
    unittest.main()
