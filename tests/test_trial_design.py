from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from mind_virus.experiment_spec import (
    ClaimSpec, GeneralizedExperimentSpec, InterventionSpec, NetworkSpec,
)
from mind_virus.trial_design import plan_matched_trials


def design(seed: int = 2026) -> GeneralizedExperimentSpec:
    return GeneralizedExperimentSpec(
        "matched-pilot", seed, 3, NetworkSpec("ring", 8),
        (
            ClaimSpec("bakery", "bakery", "The bakery has free bread."),
            ClaimSpec("bus", "bus", "The bus stop is closed."),
        ),
        (
            InterventionSpec("none"),
            InterventionSpec("skepticism", 0.35),
            InterventionSpec("fact_check", 0.5),
        ),
    )


class TrialDesignTests(unittest.TestCase):
    def test_manifest_contains_every_configured_trial(self):
        manifest = plan_matched_trials(design())
        self.assertEqual(len(manifest.trials), 18)
        self.assertEqual(len(manifest.trials), design().planned_trials)

    def test_execution_indexes_are_contiguous(self):
        manifest = plan_matched_trials(design())
        self.assertEqual(
            [trial.execution_index for trial in manifest.trials], list(range(18))
        )

    def test_same_seed_produces_identical_manifest(self):
        self.assertEqual(plan_matched_trials(design()), plan_matched_trials(design()))

    def test_different_seed_changes_randomized_order(self):
        first = [trial.matched_trial_id for trial in plan_matched_trials(design(1)).trials]
        second = [trial.matched_trial_id for trial in plan_matched_trials(design(2)).trials]
        self.assertNotEqual(first, second)

    def test_matched_conditions_share_assignment_and_network_seeds(self):
        manifest = plan_matched_trials(design())
        groups: dict[str, list] = {}
        for trial in manifest.trials:
            groups.setdefault(trial.matched_trial_id, []).append(trial)
        for trials in groups.values():
            self.assertEqual(len({trial.assignment_seed for trial in trials}), 1)
            self.assertEqual(len({trial.network_seed for trial in trials}), 1)
            self.assertEqual(len(trials), 3)

    def test_each_condition_trial_is_unique(self):
        manifest = plan_matched_trials(design())
        keys = {
            (trial.claim_id, trial.intervention_type,
             trial.intervention_intensity, trial.repetition)
            for trial in manifest.trials
        }
        self.assertEqual(len(keys), len(manifest.trials))

    def test_manifest_records_specification_fingerprint(self):
        spec = design()
        manifest = plan_matched_trials(spec)
        self.assertTrue(all(
            trial.specification_fingerprint == spec.fingerprint
            for trial in manifest.trials
        ))

    def test_manifest_can_be_saved_for_audit(self):
        with TemporaryDirectory() as directory:
            path = plan_matched_trials(design()).save(Path(directory) / "manifest.json")
            payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(len(payload["trials"]), 18)
        self.assertEqual(payload["experiment_name"], "matched-pilot")


if __name__ == "__main__":
    unittest.main()
