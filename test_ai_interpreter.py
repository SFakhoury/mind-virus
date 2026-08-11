import unittest

from agent import Agent
from ai_interpreter import OpenAIInterpreter


class FakeResponse:
    def __init__(self, output_text: str) -> None:
        self.output_text = output_text


class FakeResponses:
    def __init__(self, output_text: str) -> None:
        self.output_text = output_text
        self.last_request = None

    def create(self, **kwargs):
        self.last_request = kwargs
        return FakeResponse(self.output_text)


class FakeClient:
    def __init__(self, output_text: str) -> None:
        self.responses = FakeResponses(output_text)


class OpenAIInterpreterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.alice = Agent(
            name="Alice",
            personality="Excitable and highly trusting",
        )
        self.bob = Agent(
            name="Bob",
            personality="Cautious and evidence-seeking",
        )

    def test_interpreter_returns_model_output(self) -> None:
        client = FakeClient(
            "Alice claimed that the bakery might have free bread."
        )
        interpreter = OpenAIInterpreter(
            model="test-model",
            client=client,
        )

        result = interpreter(
            listener=self.bob,
            speaker=self.alice,
            message=(
                "The bakery is giving away free bread."
            ),
        )

        self.assertEqual(
            result,
            (
                "Alice claimed that the bakery might "
                "have free bread."
            ),
        )

    def test_request_contains_agent_context(self) -> None:
        self.bob.observe(
            event="The bakery charged normal prices yesterday.",
            importance=7,
        )

        client = FakeClient(
            "I remember Alice making an uncertain claim."
        )
        interpreter = OpenAIInterpreter(
            model="test-model",
            client=client,
        )

        interpreter(
            listener=self.bob,
            speaker=self.alice,
            message="The bakery now has free bread.",
        )

        request = client.responses.last_request
        prompt = request["input"]

        self.assertEqual(request["model"], "test-model")
        self.assertIn("Bob", prompt)
        self.assertIn(
            "Cautious and evidence-seeking",
            prompt,
        )
        self.assertIn("Alice", prompt)
        self.assertIn("free bread", prompt)
        self.assertIn("normal prices yesterday", prompt)

    def test_prompt_preserves_hearsay_distinction(self) -> None:
        client = FakeClient("An attributed memory.")
        interpreter = OpenAIInterpreter(
            client=client,
        )

        interpreter(
            listener=self.bob,
            speaker=self.alice,
            message="The bakery has free bread.",
        )

        instructions = (
            client.responses.last_request["instructions"]
        )

        self.assertIn(
            "Do not convert hearsay into established fact",
            instructions,
        )

    def test_empty_model_output_is_rejected(self) -> None:
        interpreter = OpenAIInterpreter(
            client=FakeClient("   "),
        )

        with self.assertRaisesRegex(
            ValueError,
            "empty interpretation",
        ):
            interpreter(
                listener=self.bob,
                speaker=self.alice,
                message="The bakery has free bread.",
            )


if __name__ == "__main__":
    unittest.main()
