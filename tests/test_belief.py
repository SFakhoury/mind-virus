import unittest

from mind_virus.agent import Agent
from mind_virus.belief import Belief
from mind_virus.claim import Claim


class BeliefTests(unittest.TestCase):
    def setUp(self) -> None:
        self.alice = Agent(
            name="Alice",
            personality="Friendly and observant",
        )
        self.bob = Agent(
            name="Bob",
            personality="Cautious and analytical",
        )

        self.claim = Claim(
            content="The bakery is giving away free bread.",
            source_agent="Alice",
            confidence=0.8,
        )

    def test_belief_can_be_created_from_claim(self) -> None:
        belief = Belief.from_claim(self.claim)

        self.assertEqual(
            belief.topic_id,
            self.claim.topic_id,
        )
        self.assertEqual(belief.claim_id, self.claim.id)
        self.assertEqual(belief.content, self.claim.content)
        self.assertEqual(belief.confidence, 0.8)

    def test_agent_accepts_claim_above_threshold(self) -> None:
        belief = self.bob.consider_claim(
            self.claim,
            acceptance_threshold=0.6,
        )

        self.assertIsNotNone(belief)
        self.assertTrue(
            self.bob.believes(self.claim.topic_id)
        )

    def test_agent_rejects_claim_below_threshold(self) -> None:
        belief = self.bob.consider_claim(
            self.claim,
            acceptance_threshold=0.9,
        )

        self.assertIsNone(belief)
        self.assertFalse(
            self.bob.believes(self.claim.topic_id)
        )

    def test_hearing_does_not_automatically_create_belief(
        self,
    ) -> None:
        self.bob.hear(
            speaker=self.alice,
            message=self.claim.content,
            importance=6,
        )

        self.assertEqual(len(self.bob.memories), 1)
        self.assertFalse(
            self.bob.believes(self.claim.topic_id)
        )

    def test_agent_can_evaluate_confidence_independently(
        self,
    ) -> None:
        belief = self.bob.consider_claim(
            self.claim,
            acceptance_threshold=0.5,
            belief_confidence=0.55,
        )

        self.assertIsNotNone(belief)
        self.assertEqual(belief.confidence, 0.55)
        self.assertNotEqual(
            belief.confidence,
            self.claim.confidence,
        )

    def test_believing_agent_can_repeat_claim(self) -> None:
        self.bob.consider_claim(
            self.claim,
            acceptance_threshold=0.5,
        )

        repeated = self.bob.repeat_claim(
            topic_id=self.claim.topic_id,
            content=(
                "Alice said the bakery may be giving away bread."
            ),
            confidence=0.65,
        )

        self.assertEqual(
            repeated.topic_id,
            self.claim.topic_id,
        )
        self.assertEqual(repeated.parent_id, self.claim.id)
        self.assertEqual(repeated.generation, 1)
        self.assertEqual(repeated.source_agent, "Bob")

    def test_agent_cannot_repeat_rejected_claim(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "does not believe",
        ):
            self.bob.repeat_claim(
                topic_id=self.claim.topic_id,
                content="Unaccepted claim",
                confidence=0.5,
            )


class PropagationTests(unittest.TestCase):
    def test_multi_agent_claim_lineage(self) -> None:
        alice = Agent(
            name="Alice",
            personality="Observant",
        )
        bob = Agent(
            name="Bob",
            personality="Trusting",
        )
        charlie = Agent(
            name="Charlie",
            personality="Skeptical",
        )

        original = Claim(
            content="The bakery is giving away free bread.",
            source_agent=alice.name,
            confidence=0.85,
        )

        bob.hear(
            speaker=alice,
            message=original.content,
            importance=7,
        )
        bob.consider_claim(
            original,
            acceptance_threshold=0.5,
        )

        repeated = bob.repeat_claim(
            topic_id=original.topic_id,
            content="The bakery probably has free bread.",
            confidence=0.65,
        )

        charlie.hear(
            speaker=bob,
            message=repeated.content,
            importance=5,
        )
        charlie_belief = charlie.consider_claim(
            repeated,
            acceptance_threshold=0.8,
        )

        self.assertTrue(
            bob.believes(original.topic_id)
        )
        self.assertFalse(
            charlie.believes(original.topic_id)
        )
        self.assertIsNone(charlie_belief)
        self.assertEqual(repeated.parent_id, original.id)
        self.assertEqual(repeated.generation, 1)


if __name__ == "__main__":
    unittest.main()

