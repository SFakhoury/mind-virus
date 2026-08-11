import unittest

from agent import Agent
from conversation import Conversation


class ConversationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.alice = Agent(
            name="Alice",
            personality="Friendly and observant",
        )
        self.bob = Agent(
            name="Bob",
            personality="Cautious and analytical",
        )

    def test_conversation_delivers_interpreted_memory(self) -> None:
        def interpreter(
            listener: Agent,
            speaker: Agent,
            message: str,
        ) -> str:
            return (
                "Alice noticed that the bakery seemed "
                "busier than usual."
            )

        conversation = Conversation(interpreter)
        memory = conversation.deliver(
            speaker=self.alice,
            listener=self.bob,
            message="The bakery was unusually crowded.",
            importance=6,
        )

        self.assertEqual(memory.source, "dialogue")
        self.assertIn(
            "bakery seemed busier than usual",
            memory.content,
        )

    def test_memory_remains_private_to_listener(self) -> None:
        conversation = Conversation(
            lambda listener, speaker, message: message
        )

        conversation.deliver(
            speaker=self.alice,
            listener=self.bob,
            message="The bakery was crowded.",
            importance=5,
        )

        self.assertEqual(len(self.alice.memories), 0)
        self.assertEqual(len(self.bob.memories), 1)

    def test_listeners_can_interpret_same_message_differently(
        self,
    ) -> None:
        charlie = Agent(
            name="Charlie",
            personality="Excitable and dramatic",
        )

        def interpreter(
            listener: Agent,
            speaker: Agent,
            message: str,
        ) -> str:
            return (
                f"As someone who is {listener.personality.lower()}, "
                f"I interpreted this report as: {message}"
            )

        conversation = Conversation(interpreter)

        bob_memory = conversation.deliver(
            speaker=self.alice,
            listener=self.bob,
            message="The bakery had a long line.",
            importance=5,
        )
        charlie_memory = conversation.deliver(
            speaker=self.alice,
            listener=charlie,
            message="The bakery had a long line.",
            importance=5,
        )

        self.assertNotEqual(
            bob_memory.content,
            charlie_memory.content,
        )

    def test_complete_memory_conversation_loop(self) -> None:
        observed = self.alice.observe(
            event="The bakery was crowded this morning.",
            importance=7,
        )

        alice_recall = self.alice.recall(
            context="bakery crowd",
            limit=1,
        )

        conversation = Conversation(
            lambda listener, speaker, message: (
                "Alice reported that the bakery was busy."
            )
        )

        conversation.deliver(
            speaker=self.alice,
            listener=self.bob,
            message=alice_recall[0].content,
            importance=6,
        )

        bob_recall = self.bob.recall(
            context="Alice bakery",
            limit=1,
        )

        self.assertEqual(alice_recall, [observed])
        self.assertEqual(len(bob_recall), 1)
        self.assertIn("bakery was busy", bob_recall[0].content)

    def test_conversation_rejects_invalid_inputs(self) -> None:
        with self.assertRaisesRegex(
            TypeError,
            "Interpreter must be callable",
        ):
            Conversation(None)

        conversation = Conversation(
            lambda listener, speaker, message: message
        )

        with self.assertRaisesRegex(
            ValueError,
            "message cannot be empty",
        ):
            conversation.deliver(
                speaker=self.alice,
                listener=self.bob,
                message="   ",
                importance=5,
            )


if __name__ == "__main__":
    unittest.main()
