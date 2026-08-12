import unittest

from mind_virus.agent import Agent
from mind_virus.decision import (
    OpenAIDecisionMaker,
    TransmissionDecision,
)


class FakeResponse:
    def __init__(self, decision):
        self.output_parsed = decision


class FakeResponses:
    def __init__(self, decision):
        self.decision = decision
        self.request = None

    def parse(self, **kwargs):
        self.request = kwargs
        return FakeResponse(self.decision)


class FakeClient:
    def __init__(self, decision):
        self.responses = FakeResponses(decision)


class DecisionTests(unittest.TestCase):
    def test_structured_decision_is_returned(self) -> None:
        expected = TransmissionDecision(
            remembered_message=(
                "Alice said she heard the bakery "
                "might have free bread."
            ),
            believes_claim=False,
            repeats_claim=False,
            belief_confidence=0.2,
            reason="There is no supporting evidence.",
        )
        client = FakeClient(expected)
        maker = OpenAIDecisionMaker(
            client=client,
            model="test-model",
        )

        alice = Agent("Alice", "Trusting")
        bob = Agent("Bob", "Skeptical")

        result = maker(bob, alice, "Free bread.")

        self.assertEqual(result, expected)
        self.assertIn(
            "Speaker name: Alice",
            client.responses.request["input"],
        )

    def test_confidence_is_validated(self) -> None:
        with self.assertRaises(ValueError):
            TransmissionDecision(
                remembered_message="A memory",
                believes_claim=True,
                repeats_claim=True,
                belief_confidence=1.5,
                reason="Invalid confidence",
            )


if __name__ == "__main__":
    unittest.main()
