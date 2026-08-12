from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from mind_virus.output_review import (
    RawOutputRecord, ReviewDecision, create_blinded_review_packet,
    measure_review_agreement, save_review_packet,
)


def records():
    return [
        RawOutputRecord("r1", "model-a", "baseline", "bakery", "memory A", "output A"),
        RawOutputRecord("r2", "model-b", "skeptical", "bus", "memory B", "output B"),
        RawOutputRecord("r3", "model-a", "baseline", "library", "memory C", "output C"),
    ]


class OutputReviewTests(unittest.TestCase):
    def test_packet_hides_model_condition_and_claim_labels(self):
        packet, _ = create_blinded_review_packet(records())
        serialized = json.dumps([item.__dict__ for item in packet])
        self.assertNotIn("model-a", serialized)
        self.assertNotIn("baseline", serialized)
        self.assertNotIn("bakery", serialized)

    def test_private_key_preserves_hidden_provenance(self):
        packet, key = create_blinded_review_packet(records())
        self.assertEqual(set(key), {item.review_id for item in packet})
        self.assertEqual({value["record_id"] for value in key.values()}, {"r1", "r2", "r3"})

    def test_packet_order_and_ids_are_reproducible(self):
        self.assertEqual(
            create_blinded_review_packet(records(), seed=9),
            create_blinded_review_packet(records(), seed=9),
        )

    def test_duplicate_raw_ids_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "unique"):
            create_blinded_review_packet([records()[0], records()[0]])

    def test_packet_and_key_are_saved_separately(self):
        packet, key = create_blinded_review_packet(records())
        with TemporaryDirectory() as directory:
            packet_path, key_path = save_review_packet(
                packet, key, Path(directory) / "packet.json", Path(directory) / "key.json"
            )
            self.assertNotIn("condition", packet_path.read_text(encoding="utf-8"))
            self.assertIn("condition", key_path.read_text(encoding="utf-8"))

    def test_perfect_agreement_has_kappa_one(self):
        first = [ReviewDecision("a", "reviewer-1", "supported"),
                 ReviewDecision("b", "reviewer-1", "unsupported")]
        second = [ReviewDecision("a", "reviewer-2", "supported"),
                  ReviewDecision("b", "reviewer-2", "unsupported")]
        result = measure_review_agreement(first, second)
        self.assertEqual(result.exact_agreement, 1.0)
        self.assertEqual(result.cohens_kappa, 1.0)

    def test_disagreements_are_flagged_for_adjudication(self):
        first = [ReviewDecision("a", "one", "supported"),
                 ReviewDecision("b", "one", "unsupported")]
        second = [ReviewDecision("a", "two", "unclear"),
                  ReviewDecision("b", "two", "unsupported")]
        result = measure_review_agreement(first, second)
        self.assertEqual(result.disagreements, ("a",))
        self.assertEqual(result.exact_agreement, 0.5)

    def test_reviewers_must_judge_same_items(self):
        with self.assertRaisesRegex(ValueError, "same"):
            measure_review_agreement(
                [ReviewDecision("a", "one", "supported")],
                [ReviewDecision("b", "two", "supported")],
            )

    def test_invalid_review_label_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "label"):
            ReviewDecision("a", "reviewer", "maybe")


if __name__ == "__main__":
    unittest.main()
