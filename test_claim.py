import unittest

from claim import Claim


class ClaimTests(unittest.TestCase):
    def test_original_claim_gets_unique_identity(self) -> None:
        claim = Claim(
            content="The bakery is giving away free bread.",
            source_agent="Alice",
            confidence=0.8,
        )

        self.assertTrue(claim.id)
        self.assertTrue(claim.topic_id)
        self.assertEqual(claim.generation, 0)
        self.assertIsNone(claim.parent_id)

    def test_transmission_preserves_topic_and_tracks_parent(
        self,
    ) -> None:
        original = Claim(
            content="The bakery is giving away free bread.",
            source_agent="Alice",
            confidence=0.8,
        )

        transmitted = original.transmit(
            content="Alice said the bakery may have free bread.",
            source_agent="Bob",
            confidence=0.6,
        )

        self.assertNotEqual(transmitted.id, original.id)
        self.assertEqual(
            transmitted.topic_id,
            original.topic_id,
        )
        self.assertEqual(transmitted.parent_id, original.id)
        self.assertEqual(transmitted.generation, 1)
        self.assertEqual(transmitted.source_agent, "Bob")

    def test_multiple_generations_form_a_lineage(self) -> None:
        generation_zero = Claim(
            content="The bakery is giving away free bread.",
            source_agent="Alice",
            confidence=0.9,
        )
        generation_one = generation_zero.transmit(
            content="The bakery might have free bread.",
            source_agent="Bob",
            confidence=0.7,
        )
        generation_two = generation_one.transmit(
            content="Someone heard the bakery has free food.",
            source_agent="Charlie",
            confidence=0.5,
        )

        self.assertEqual(generation_two.generation, 2)
        self.assertEqual(
            generation_two.topic_id,
            generation_zero.topic_id,
        )
        self.assertEqual(
            generation_two.parent_id,
            generation_one.id,
        )

    def test_claim_validates_confidence(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "confidence must be between 0 and 1",
        ):
            Claim(
                content="Invalid claim",
                source_agent="Alice",
                confidence=1.5,
            )

    def test_claim_validates_generation_and_parent(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "cannot be negative",
        ):
            Claim(
                content="Invalid claim",
                source_agent="Alice",
                confidence=0.5,
                generation=-1,
            )

        with self.assertRaisesRegex(
            ValueError,
            "must have a parent",
        ):
            Claim(
                content="Missing parent",
                source_agent="Bob",
                confidence=0.5,
                generation=1,
            )

    def test_claim_is_immutable(self) -> None:
        claim = Claim(
            content="The bakery is crowded.",
            source_agent="Alice",
            confidence=0.7,
        )

        with self.assertRaises(AttributeError):
            claim.content = "Changed claim"


if __name__ == "__main__":
    unittest.main()
