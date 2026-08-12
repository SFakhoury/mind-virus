from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from mind_virus.experiment_spec import (
    ClaimSpec, GeneralizedExperimentSpec, InterventionSpec, NetworkSpec,
)


def sample_spec() -> GeneralizedExperimentSpec:
    return GeneralizedExperimentSpec(
        name="network-comparison-pilot",
        seed=2026,
        trials_per_condition=5,
        network=NetworkSpec("small_world", 12, 0.2),
        claims=(
            ClaimSpec("bakery", "bakery promotion", "The bakery has free bread."),
            ClaimSpec(
                "bus", "bus route", "The market stop is closed.", "correction",
                "The transit notice says the market stop remains open.",
            ),
        ),
        interventions=(
            InterventionSpec("none", 0.0),
            InterventionSpec("skepticism", 0.35),
        ),
    )


class GeneralizedExperimentSpecTests(unittest.TestCase):
    def test_planned_trials_cover_full_design(self):
        self.assertEqual(sample_spec().planned_trials, 20)

    def test_fingerprint_is_stable(self):
        self.assertEqual(sample_spec().fingerprint, sample_spec().fingerprint)

    def test_save_and_load_preserve_exact_specification(self):
        with TemporaryDirectory() as directory:
            path = sample_spec().save(Path(directory) / "experiment.json")
            restored = GeneralizedExperimentSpec.load(path)
        self.assertEqual(restored, sample_spec())

    def test_modified_saved_spec_fails_fingerprint_check(self):
        with TemporaryDirectory() as directory:
            path = sample_spec().save(Path(directory) / "experiment.json")
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["seed"] = 99
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "fingerprint"):
                GeneralizedExperimentSpec.load(path)

    def test_non_small_world_network_rejects_rewiring(self):
        with self.assertRaisesRegex(ValueError, "small-world"):
            NetworkSpec("chain", 8, 0.2)

    def test_evidence_condition_requires_evidence_text(self):
        with self.assertRaisesRegex(ValueError, "requires evidence"):
            ClaimSpec("claim", "topic", "message", "correction")

    def test_control_rejects_nonzero_intensity(self):
        with self.assertRaisesRegex(ValueError, "zero intensity"):
            InterventionSpec("none", 0.5)

    def test_duplicate_claim_ids_are_rejected(self):
        claim = ClaimSpec("same", "topic", "message")
        with self.assertRaisesRegex(ValueError, "unique"):
            GeneralizedExperimentSpec(
                "invalid", 1, 1, NetworkSpec("chain", 4), (claim, claim),
                (InterventionSpec("none"),),
            )


if __name__ == "__main__":
    unittest.main()
