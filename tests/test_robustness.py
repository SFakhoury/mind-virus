from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from mind_virus.experiment_spec import (
    ClaimSpec, GeneralizedExperimentSpec, InterventionSpec, NetworkSpec,
)
from mind_virus.robustness import RobustnessSpec, build_robustness_manifest


def experiment(seed: int = 2026):
    return GeneralizedExperimentSpec(
        "robustness-pilot", seed, 2, NetworkSpec("ring", 8),
        (ClaimSpec("bakery", "bakery", "The bakery has free bread."),),
        (InterventionSpec("none"), InterventionSpec("skepticism", 0.35)),
    )


class RobustnessTests(unittest.TestCase):
    def setUp(self):
        self.spec = RobustnessSpec(
            ("model-a", "model-b"), ("neutral", "strict"), (0.0, 0.7), 2
        )

    def test_cell_count_crosses_every_axis(self):
        self.assertEqual(self.spec.cell_count, 16)
        self.assertEqual(len(build_robustness_manifest(experiment(), self.spec).cells), 16)

    def test_every_combination_is_unique(self):
        cells = build_robustness_manifest(experiment(), self.spec).cells
        combinations = {
            (cell.model, cell.prompt_variant, cell.temperature, cell.repetition)
            for cell in cells
        }
        self.assertEqual(len(combinations), 16)

    def test_manifest_is_reproducible(self):
        self.assertEqual(
            build_robustness_manifest(experiment(), self.spec),
            build_robustness_manifest(experiment(), self.spec),
        )

    def test_changed_experiment_seed_changes_cell_seeds(self):
        first = build_robustness_manifest(experiment(1), self.spec)
        second = build_robustness_manifest(experiment(2), self.spec)
        self.assertNotEqual(
            [cell.seed for cell in first.cells], [cell.seed for cell in second.cells]
        )

    def test_invalid_temperature_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "between 0 and 2"):
            RobustnessSpec(("model",), ("prompt",), (2.5,))

    def test_duplicate_axis_values_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "unique"):
            RobustnessSpec(("model", "model"), ("prompt",), (0.0,))

    def test_manifest_can_be_saved_for_audit(self):
        with TemporaryDirectory() as directory:
            manifest = build_robustness_manifest(experiment(), self.spec)
            path = manifest.save(Path(directory) / "robustness.json")
            payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(len(payload["cells"]), 16)
        self.assertEqual(payload["experiment_fingerprint"], experiment().fingerprint)


if __name__ == "__main__":
    unittest.main()
