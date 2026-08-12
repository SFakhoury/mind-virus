import unittest

from mind_virus.research_metrics import (
    measure_calibration, measure_claim_mutation, measure_network_propagation,
)


class ResearchMetricsTests(unittest.TestCase):
    def test_unchanged_claim_has_perfect_similarity(self):
        result = measure_claim_mutation(["The bakery is open.", "The bakery is open."])
        self.assertEqual(result.final_similarity, 1.0)
        self.assertEqual(result.introduced_terms, ())
        self.assertEqual(result.lost_terms, ())

    def test_mutation_records_lost_and_introduced_terms(self):
        result = measure_claim_mutation([
            "The bakery has free bread.", "The bakery has discounted cake."
        ])
        self.assertIn("bread", result.lost_terms)
        self.assertIn("cake", result.introduced_terms)
        self.assertLess(result.final_similarity, 1.0)

    def test_multi_step_mutation_counts_transmissions(self):
        result = measure_claim_mutation(["a b c", "a b d", "a d e"])
        self.assertEqual(result.transmissions, 2)
        self.assertGreaterEqual(result.average_step_similarity, 0.0)

    def test_perfect_confidence_predictions_have_zero_calibration_error(self):
        result = measure_calibration([0.0, 1.0], [False, True])
        self.assertEqual(result.brier_score, 0.0)
        self.assertEqual(result.expected_calibration_error, 0.0)

    def test_wrong_confident_predictions_have_maximum_brier_score(self):
        result = measure_calibration([1.0, 0.0], [False, True])
        self.assertEqual(result.brier_score, 1.0)

    def test_calibration_samples_must_be_paired(self):
        with self.assertRaisesRegex(ValueError, "paired"):
            measure_calibration([0.5], [True, False])

    def test_network_metrics_measure_reach_and_edge_coverage(self):
        result = measure_network_propagation(
            exposed_nodes={0, 1, 2}, total_nodes=5,
            transmission_edges=[(0, 1), (1, 2)], total_network_edges=5,
            maximum_generation=2,
        )
        self.assertEqual(result.reach_fraction, 0.6)
        self.assertEqual(result.edge_coverage, 0.4)

    def test_repeated_transmission_edge_is_counted_once(self):
        result = measure_network_propagation(
            exposed_nodes={0, 1}, total_nodes=4,
            transmission_edges=[(0, 1), (1, 0)], total_network_edges=3,
            maximum_generation=1,
        )
        self.assertEqual(result.unique_transmission_edges, 1)

    def test_unknown_exposed_node_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "belong"):
            measure_network_propagation(
                exposed_nodes={0, 5}, total_nodes=4,
                transmission_edges=[], total_network_edges=3,
                maximum_generation=0,
            )


if __name__ == "__main__":
    unittest.main()
