import unittest

from agent import Agent


class ListenerInterpretationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.alice = Agent(
            name="Alice",
            personality="Friendly, curious, and observant",
        )
        self.bob = Agent(
            name="Bob",
            personality="Reserved, cautious, and analytical",
        )

    def test_listener_can_store_an_interpretation(self) -> None:
        spoken_message = (
            "The bakery was unusually crowded this morning."
        )
        bob_interpretation = (
            "Alice noticed that the bakery seemed busier than usual."
        )

        memory = self.bob.hear(
            speaker=self.alice,
            message=spoken_message,
            importance=6,
            interpretation=bob_interpretation,
        )

        self.assertEqual(memory.source, "dialogue")
        self.assertIn("Alice", memory.content)
        self.assertIn(bob_interpretation, memory.content)
        self.assertNotIn(spoken_message, memory.content)

    def test_different_listeners_can_remember_differently(self) -> None:
        charlie = Agent(
            name="Charlie",
            personality="Excitable and prone to exaggeration",
        )
        spoken_message = "The bakery had a long line."

        bob_memory = self.bob.hear(
            speaker=self.alice,
            message=spoken_message,
            importance=5,
            interpretation=(
                "Alice saw that the bakery was somewhat busy."
            ),
        )
        charlie_memory = charlie.hear(
            speaker=self.alice,
            message=spoken_message,
            importance=8,
            interpretation=(
                "Alice saw an enormous crowd at the bakery."
            ),
        )

        self.assertNotEqual(
            bob_memory.content,
            charlie_memory.content,
        )
        self.assertEqual(len(self.bob.memories), 1)
        self.assertEqual(len(charlie.memories), 1)

    def test_interpretation_does_not_change_speaker_memory(self) -> None:
        self.bob.hear(
            speaker=self.alice,
            message="The bakery had a long line.",
            importance=5,
            interpretation="The bakery seemed busy.",
        )

        self.assertEqual(len(self.alice.memories), 0)
        self.assertEqual(len(self.bob.memories), 1)

    def test_empty_interpretation_is_rejected(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "interpretation cannot be empty",
        ):
            self.bob.hear(
                speaker=self.alice,
                message="The bakery was crowded.",
                importance=5,
                interpretation="   ",
            )


if __name__ == "__main__":
    unittest.main()
