from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from mind_virus.experiment_framework import (
    GeneralizedExperimentRunner, estimate_two_proportion_sample_size,
)
from mind_virus.experiment_spec import (
    ClaimSpec, GeneralizedExperimentSpec, InterventionSpec, NetworkSpec,
)
from mind_virus.preregistration import PreregisteredHypothesis, freeze_preregistration


def specification(stage: str = "pilot") -> GeneralizedExperimentSpec:
    return GeneralizedExperimentSpec(
        "generalized-study", 2026, 2, NetworkSpec("ring", 6),
        (ClaimSpec("bakery", "bakery", "The bakery has free bread."),),
        (InterventionSpec("none"), InterventionSpec("skepticism", 0.4)),
        dataset_stage=stage,
    )


def outcomes(context):
    treated_effect = 0.25 if context.assignment.treated_positions else 0.0
    return {
        "exposed_agents": float(len(context.network.nodes)),
        "maximum_generation": 3.0,
        "repetition_rate": 1.0 - treated_effect,
        "belief_rate": 0.5 - treated_effect,
    }


class GeneralizedExperimentRunnerTests(unittest.TestCase):
    def test_runner_executes_full_configuration(self):
        results = GeneralizedExperimentRunner(specification(), outcomes).run()
        self.assertEqual(len(results), 4)
        self.assertEqual({item.intervention_type for item in results}, {"none", "skepticism"})

    def test_matched_results_share_network_and_assignment_seeds(self):
        results = GeneralizedExperimentRunner(specification(), outcomes).run()
        groups = {}
        for result in results:
            groups.setdefault(result.matched_trial_id, []).append(result)
        for group in groups.values():
            self.assertEqual(len({item.network_seed for item in group}), 1)
            self.assertEqual(len({item.assignment_seed for item in group}), 1)

    def test_wrong_outcome_schema_is_rejected(self):
        runner = GeneralizedExperimentRunner(specification(), lambda context: {"wrong": 1.0})
        with self.assertRaisesRegex(ValueError, "frozen outcome"):
            runner.run()

    def test_nonfinite_outcome_is_rejected(self):
        def invalid(context):
            result = outcomes(context)
            result["belief_rate"] = float("nan")
            return result
        with self.assertRaisesRegex(ValueError, "finite"):
            GeneralizedExperimentRunner(specification(), invalid).run()

    def test_pilot_and_confirmatory_outputs_use_separate_directories(self):
        with TemporaryDirectory() as directory:
            runner = GeneralizedExperimentRunner(specification(), outcomes)
            path = runner.save(runner.run(), directory)
            self.assertEqual(path.parent.name, "pilot")

    def test_confirmatory_run_requires_matching_preregistration(self):
        confirmatory = specification("confirmatory")
        with TemporaryDirectory() as directory:
            path = freeze_preregistration(
                confirmatory,
                (PreregisteredHypothesis(
                    "H1", "skepticism", "belief_rate", "Belief decreases.", True
                ),),
                Path(directory) / "pre.json",
            )
            results = GeneralizedExperimentRunner(
                confirmatory, outcomes, preregistration_path=path
            ).run()
        self.assertEqual(len(results), 4)

    def test_confirmatory_run_without_preregistration_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "require"):
            GeneralizedExperimentRunner(specification("confirmatory"), outcomes)

    def test_saved_dataset_contains_provenance(self):
        with TemporaryDirectory() as directory:
            runner = GeneralizedExperimentRunner(specification(), outcomes)
            path = runner.save(runner.run(), directory)
            payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(payload["specification_fingerprint"], specification().fingerprint)
        self.assertEqual(len(payload["results"]), 4)

    def test_power_estimate_is_positive_and_effect_sensitive(self):
        large_effect = estimate_two_proportion_sample_size(0.5, 0.25)
        small_effect = estimate_two_proportion_sample_size(0.5, 0.4)
        self.assertGreater(large_effect, 0)
        self.assertGreater(small_effect, large_effect)

    def test_zero_expected_effect_has_no_finite_sample_plan(self):
        with self.assertRaisesRegex(ValueError, "nonzero"):
            estimate_two_proportion_sample_size(0.5, 0.5)


if __name__ == "__main__":
    unittest.main()
