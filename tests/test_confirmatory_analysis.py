import unittest

from scripts.analyze_confirmatory_experiment import analyze_records


class ConfirmatoryAnalysisTests(unittest.TestCase):
    def make_records(self):
        records = []

        for trial in range(2):
            records.extend([
                {
                    "claim_id": "claim_a",
                    "trial": trial,
                    "condition": "baseline",
                    "exposed_agents": 4,
                    "maximum_generation": 3,
                    "repetition_rate": 1.0,
                    "belief_rate": 0.5,
                },
                {
                    "claim_id": "claim_a",
                    "trial": trial,
                    "condition": "skeptical",
                    "exposed_agents": 3,
                    "maximum_generation": 2,
                    "repetition_rate": 0.5,
                    "belief_rate": 0.25,
                },
            ])

        return records

    def test_analysis_calculates_skeptical_minus_baseline(self):
        results = analyze_records(self.make_records())
        exposure = results["by_claim"]["claim_a"]["exposed_agents"]

        self.assertEqual(exposure["sample_size"], 2)
        self.assertEqual(exposure["baseline_mean"], 4)
        self.assertEqual(exposure["skeptical_mean"], 3)
        self.assertEqual(exposure["mean_difference"], -1)

    def test_analysis_produces_pooled_results(self):
        results = analyze_records(self.make_records())

        self.assertIn("exposed_agents", results["pooled"])
        self.assertIn("maximum_generation", results["pooled"])
        self.assertIn("repetition_rate", results["pooled"])
        self.assertIn("belief_rate", results["pooled"])

    def test_analysis_rejects_missing_condition(self):
        records = self.make_records()
        records.pop()

        with self.assertRaises(ValueError):
            analyze_records(records)


if __name__ == "__main__":
    unittest.main()
