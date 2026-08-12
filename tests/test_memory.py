import unittest
from datetime import datetime, timedelta, timezone

from mind_virus.memory import Memory, MemoryStream


class MemoryTests(unittest.TestCase):
    def test_memory_validates_content(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "cannot be empty",
        ):
            Memory("   ", 5, "observation")

    def test_memory_validates_importance(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "between 1 and 10",
        ):
            Memory(
                "Invalid importance",
                11,
                "observation",
            )


class MemoryStreamTests(unittest.TestCase):
    def test_add_all_recent_and_len(self) -> None:
        stream = MemoryStream()

        first = Memory(
            "First memory",
            2,
            "observation",
        )
        second = Memory(
            "Second memory",
            4,
            "dialogue",
        )

        stream.add(first)
        stream.add(second)

        self.assertEqual(len(stream), 2)
        self.assertEqual(stream.all(), [first, second])
        self.assertEqual(stream.recent(1), [second])

    def test_lexical_relevance_uses_word_overlap(self) -> None:
        related = MemoryStream._lexical_relevance(
            "crowded bakery",
            "The bakery was crowded",
        )
        unrelated = MemoryStream._lexical_relevance(
            "crowded bakery",
            "The park was quiet",
        )

        self.assertGreater(related, unrelated)
        self.assertEqual(unrelated, 0.0)

    def test_score_combines_three_signals(self) -> None:
        now = datetime.now(timezone.utc)

        memory = Memory(
            "The bakery was crowded",
            8,
            "observation",
            created_at=now - timedelta(hours=24),
        )

        score = MemoryStream._score(
            memory,
            "crowded bakery",
            now,
        )

        expected_recency = 0.36787944117144233
        expected_importance = 0.8
        expected_relevance = 0.5

        self.assertAlmostEqual(
            score,
            expected_recency
            + expected_importance
            + expected_relevance,
        )

    def test_retrieve_ranks_by_combined_score(self) -> None:
        now = datetime.now(timezone.utc)
        stream = MemoryStream()

        old_relevant = Memory(
            "The bakery was crowded",
            5,
            "observation",
            created_at=now - timedelta(days=7),
        )
        recent_important = Memory(
            "Alice discussed the town square",
            10,
            "dialogue",
            created_at=now,
        )

        stream.add(old_relevant)
        stream.add(recent_important)

        results = stream.retrieve(
            "bakery crowd",
            limit=2,
        )

        self.assertEqual(results[0], recent_important)
        self.assertEqual(results[1], old_relevant)

    def test_retrieve_validates_arguments(self) -> None:
        stream = MemoryStream()

        with self.assertRaisesRegex(
            ValueError,
            "query cannot be empty",
        ):
            stream.retrieve("   ")

        with self.assertRaisesRegex(
            ValueError,
            "Limit must be at least 1",
        ):
            stream.retrieve("bakery", limit=0)


if __name__ == "__main__":
    unittest.main()

