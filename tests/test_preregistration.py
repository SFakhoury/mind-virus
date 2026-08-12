from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from mind_virus.experiment_spec import (
    ClaimSpec, GeneralizedExperimentSpec, InterventionSpec, NetworkSpec,
)
from mind_virus.preregistration import (
    PreregisteredHypothesis, freeze_preregistration, verify_preregistration,
)


def spec(stage: str = "confirmatory") -> GeneralizedExperimentSpec:
    return GeneralizedExperimentSpec(
        "confirmatory-network-study", 2026, 20, NetworkSpec("ring", 12),
        (ClaimSpec("bakery", "bakery", "The bakery has free bread."),),
        (InterventionSpec("none"), InterventionSpec("skepticism", 0.35)),
        dataset_stage=stage,
    )


def hypotheses() -> tuple[PreregisteredHypothesis, ...]:
    return (
        PreregisteredHypothesis(
            "H1", "skepticism", "belief_rate",
            "Skepticism lowers belief rate relative to control.", True,
        ),
        PreregisteredHypothesis(
            "H2", "skepticism", "repetition_rate",
            "Skepticism lowers repetition rate relative to control.", False,
        ),
    )


class PreregistrationTests(unittest.TestCase):
    def test_confirmatory_preregistration_is_frozen_and_verifiable(self):
        with TemporaryDirectory() as directory:
            path = freeze_preregistration(
                spec(), hypotheses(), Path(directory) / "preregistered.json"
            )
            self.assertTrue(verify_preregistration(path))

    def test_pilot_configuration_cannot_be_preregistered(self):
        with TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "confirmatory"):
                freeze_preregistration(
                    spec("pilot"), hypotheses(), Path(directory) / "pre.json"
                )

    def test_exactly_one_primary_hypothesis_is_required(self):
        invalid = tuple(
            PreregisteredHypothesis(item.id, item.intervention_type, item.outcome,
                                    item.prediction, False)
            for item in hypotheses()
        )
        with TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "Exactly one"):
                freeze_preregistration(spec(), invalid, Path(directory) / "pre.json")

    def test_hypothesis_must_use_configured_outcome(self):
        invalid = (PreregisteredHypothesis(
            "H1", "skepticism", "sentiment", "Sentiment changes.", True
        ),)
        with TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "outcome"):
                freeze_preregistration(spec(), invalid, Path(directory) / "pre.json")

    def test_unknown_outcome_has_no_silent_definition(self):
        changed = GeneralizedExperimentSpec(
            "study", 1, 1, NetworkSpec("chain", 4), spec().claims,
            spec().interventions, outcomes=("unknown_metric",),
            dataset_stage="confirmatory",
        )
        hypothesis = (PreregisteredHypothesis(
            "H1", "skepticism", "unknown_metric", "It changes.", True
        ),)
        with TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "frozen definition"):
                freeze_preregistration(changed, hypothesis, Path(directory) / "pre.json")

    def test_existing_preregistration_cannot_be_replaced(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "pre.json"
            freeze_preregistration(spec(), hypotheses(), path)
            changed = (PreregisteredHypothesis(
                "H1", "skepticism", "belief_rate", "A different prediction.", True
            ),)
            with self.assertRaises(FileExistsError):
                freeze_preregistration(spec(), changed, path)

    def test_identical_preregistration_write_is_idempotent(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "pre.json"
            first = freeze_preregistration(spec(), hypotheses(), path)
            second = freeze_preregistration(spec(), hypotheses(), path)
            self.assertEqual(first, second)

    def test_tampering_breaks_verification(self):
        with TemporaryDirectory() as directory:
            path = freeze_preregistration(spec(), hypotheses(), Path(directory) / "pre.json")
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["hypotheses"][0]["prediction"] = "Changed after collection."
            path.write_text(json.dumps(payload), encoding="utf-8")
            self.assertFalse(verify_preregistration(path))


if __name__ == "__main__":
    unittest.main()
