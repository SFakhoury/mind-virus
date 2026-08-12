import unittest

from mind_virus.statistics import paired_bootstrap


class StatisticsTests(unittest.TestCase):
    def test_negative_difference_means_skeptical_is_lower(
        self,
    ) -> None:
        estimate = paired_bootstrap(
            baseline=[4.0, 4.0, 4.0],
            skeptical=[3.0, 4.0, 3.0],
            iterations=1000,
        )

        self.assertLess(
            estimate.mean_difference,
            0.0,
        )
        self.assertEqual(estimate.sample_size, 3)

    def test_identical_samples_have_zero_effect(self) -> None:
        estimate = paired_bootstrap(
            baseline=[3.0, 4.0, 2.0],
            skeptical=[3.0, 4.0, 2.0],
            iterations=1000,
        )

        self.assertEqual(
            estimate.mean_difference,
            0.0,
        )
        self.assertEqual(
            estimate.confidence_interval_low,
            0.0,
        )
        self.assertEqual(
            estimate.confidence_interval_high,
            0.0,
        )

    def test_samples_must_be_paired(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "equal lengths",
        ):
            paired_bootstrap(
                baseline=[1.0, 2.0],
                skeptical=[1.0],
            )

    def test_bootstrap_is_reproducible(self) -> None:
        first = paired_bootstrap(
            [4.0, 4.0, 4.0],
            [3.0, 4.0, 3.0],
            iterations=1000,
            seed=50,
        )
        second = paired_bootstrap(
            [4.0, 4.0, 4.0],
            [3.0, 4.0, 3.0],
            iterations=1000,
            seed=50,
        )

        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
