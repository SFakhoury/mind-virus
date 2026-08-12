import unittest

from mind_virus.config import ExperimentConfig
from mind_virus.controlled_pilot import (
    run_controlled_pilot,
)
from mind_virus.decision import TransmissionDecision


def conditional_decision(listener, speaker, message):
    skeptical = "Skeptical" in listener.personality

    return TransmissionDecision(
        remembered_message=(
            f"{speaker.name} passed along the bakery claim."
        ),
        believes_claim=not skeptical,
        repeats_claim=not skeptical,
        belief_confidence=0.2 if skeptical else 0.7,
        reason=(
            "No evidence."
            if skeptical
            else "The speaker seemed credible."
        ),
    )


class ControlledPilotTests(unittest.TestCase):
    def test_skeptical_chain_stops_naturally(self) -> None:
        config = ExperimentConfig(
            trials_per_condition=1,
            agents_per_trial=4,
            maximum_api_calls=6,
        )

        result = run_controlled_pilot(
            config,
            conditional_decision,
        )

        self.assertEqual(
            result.maximum_generation_by_trial[
                "baseline:0"
            ],
            3,
        )
        self.assertEqual(
            result.maximum_generation_by_trial[
                "skeptical:0"
            ],
            1,
        )

    def test_hearing_does_not_require_belief(self) -> None:
        config = ExperimentConfig(
            trials_per_condition=1,
            agents_per_trial=2,
            maximum_api_calls=2,
        )

        result = run_controlled_pilot(
            config,
            conditional_decision,
        )

        skeptical = next(
            record
            for record in result.records
            if record.condition == "skeptical"
        )

        self.assertTrue(skeptical.remembered_message)
        self.assertFalse(skeptical.believes_claim)
        self.assertFalse(skeptical.repeats_claim)

    def test_early_stopping_reduces_calls(self) -> None:
        config = ExperimentConfig(
            trials_per_condition=2,
            agents_per_trial=4,
            maximum_api_calls=12,
        )

        result = run_controlled_pilot(
            config,
            conditional_decision,
        )

        self.assertEqual(result.calls_made, 8)


if __name__ == "__main__":
    unittest.main()
