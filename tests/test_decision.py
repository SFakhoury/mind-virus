import unittest

from mind_virus.agent import Agent
from mind_virus.decision import (
    ModelUsage,
    OpenAIDecisionMaker,
    TransmissionDecision,
)


class FakeUsage:
    input_tokens = 500
    output_tokens = 100


class FakeResponse:
    def __init__(self, decision):
        self.output_parsed = decision
        self.usage = FakeUsage()


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


def example_decision():
    return TransmissionDecision(
        remembered_message=(
            "Alice said she heard the bakery "
            "might have free bread."
        ),
        believes_claim=False,
        repeats_claim=False,
        belief_confidence=0.2,
        reason="There is no supporting evidence.",
    )


class DecisionTests(unittest.TestCase):
    def test_structured_decision_is_returned(self) -> None:
        expected = example_decision()
        client = FakeClient(expected)
        maker = OpenAIDecisionMaker(
            client=client,
            model="test-model",
        )

        alice = Agent("Alice", "Social")
        bob = Agent("Bob", "Careful")

        result = maker(
            bob,
            alice,
            "Free bread.",
        )

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

    def test_usage_is_accumulated(self) -> None:
        maker = OpenAIDecisionMaker(
            client=FakeClient(example_decision()),
            model="test-model",
        )
        alice = Agent("Alice", "Social")
        bob = Agent("Bob", "Careful")

        maker(bob, alice, "First claim")
        maker(bob, alice, "Second claim")

        self.assertEqual(maker.usage.calls, 2)
        self.assertEqual(
            maker.usage.input_tokens,
            1000,
        )
        self.assertEqual(
            maker.usage.output_tokens,
            200,
        )
        self.assertAlmostEqual(
            maker.usage.estimated_cost_usd,
            0.0022,
        )

    def test_model_usage_cost_calculation(self) -> None:
        usage = ModelUsage(
            calls=10,
            input_tokens=10_000,
            output_tokens=2_000,
        )

        self.assertAlmostEqual(
            usage.estimated_cost_usd,
            0.022,
        )


if __name__ == "__main__":
    unittest.main()
