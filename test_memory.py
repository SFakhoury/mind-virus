import unittest

from memory import Memory, MemoryStream


class MemoryStreamRetrievalTests(unittest.TestCase):
    def setUp(self) -> None:
        self.stream = MemoryStream()
        self.bakery = Memory("Visited the crowded bakery.", 4, "observation")
        self.park = Memory("The park was quiet today.", 9, "observation")
        self.report = Memory(
            "Alice said the bakery had a large crowd.", 7, "dialogue"
        )
        self.stream.add(self.bakery)
        self.stream.add(self.park)
        self.stream.add(self.report)

    def test_retrieve_ranks_relevance_before_importance(self) -> None:
        results = self.stream.retrieve("large bakery crowd")

        self.assertEqual(results, [self.report, self.bakery])

    def test_retrieve_uses_importance_to_break_relevance_ties(self) -> None:
        results = self.stream.retrieve("today visited")

        self.assertEqual(results, [self.park, self.bakery])

    def test_retrieve_respects_limit(self) -> None:
        self.assertEqual(self.stream.retrieve("bakery", limit=1), [self.report])

    def test_retrieve_excludes_unrelated_memories(self) -> None:
        self.assertEqual(self.stream.retrieve("library"), [])

    def test_retrieve_rejects_invalid_arguments(self) -> None:
        with self.assertRaisesRegex(ValueError, "Query cannot be empty"):
            self.stream.retrieve("   ")

        with self.assertRaisesRegex(ValueError, "Limit must be at least 1"):
            self.stream.retrieve("bakery", limit=0)


if __name__ == "__main__":
    unittest.main()
