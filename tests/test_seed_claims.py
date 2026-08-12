import unittest

from mind_virus.seed_claims import (
    SEED_CLAIMS,
    SeedClaim,
    get_seed_claim,
)


class SeedClaimTests(unittest.TestCase):
    def test_claim_ids_are_unique(self) -> None:
        ids = [
            claim.id
            for claim in SEED_CLAIMS
        ]

        self.assertEqual(
            len(ids),
            len(set(ids)),
        )

    def test_three_topics_are_configured(self) -> None:
        topics = {
            claim.topic
            for claim in SEED_CLAIMS
        }

        self.assertEqual(len(topics), 3)

    def test_claims_share_hearsay_framing(self) -> None:
        for claim in SEED_CLAIMS:
            self.assertTrue(
                claim.message.startswith("I heard")
            )

    def test_claim_can_be_retrieved_by_id(self) -> None:
        claim = get_seed_claim(
            "library_early_closure"
        )

        self.assertEqual(
            claim.topic,
            "library schedule",
        )

    def test_seed_claim_validates_fields(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "message cannot be empty",
        ):
            SeedClaim(
                id="invalid",
                topic="test",
                message="   ",
            )


if __name__ == "__main__":
    unittest.main()
