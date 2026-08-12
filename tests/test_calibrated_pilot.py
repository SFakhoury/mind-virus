import unittest

from mind_virus.calibrated_pilot import (
    run_calibrated_pilot,
)
from mind_virus.config import ExperimentConfig
from mind_virus.decision import TransmissionDecision


def mock_decision(listener, speaker, message):
    skeptical = (
        "corroborating evidence"
        in listener.personality
    )

    return TransmissionDecision(
        remembered_message=(
            f"{speaker.name} passed along the bakery claim."
        ),
        believes_claim=not skeptical,
        repeats_claim=not skeptical,
        belief_confidence=0.2 if skeptical else 0.6,
        reason=(
            "The claim lacks corroboration."
            if skeptical
            else "The claim seems plausible."
        ),
    )


class CalibratedPilotTests(unittest.TestCase):
    def test_only_assigned_skeptics_receive_treatment(
        self,
    ) -> None:
        config = ExperimentConfig(
            trials_per_condition=1,
            agents_per_trial=4,
            skeptic_fraction=0.35,
            maximum_api_calls=6,
        )

        result = run_calibrated_pilot(
            config,
            mock_decision,
        )

        skeptical_records = [
            record
            for record in result.records
            if record.condition == "skeptical"
        ]

        rejecting_records = [
            record
            for record in skeptical_records
            if not record.repeats_claim
        ]

        self.assertLessEqual(
            len(rejecting_records),
            1,
        )

    def test_baseline_is_not_explicitly_trusting(
        self,
    ) -> None:
        config = ExperimentConfig(
            trials_per_condition=1,
            agents_per_trial=3,
            maximum_api_calls=4,
        )

        observed_personalities = []

        def inspect(listener, speaker, message):
            observed_personalities.append(
                listener.personality
            )
            return mock_decision(
                listener,
                speaker,
                message,
            )

        run_calibrated_pilot(
            config,
            inspect,
        )

        self.assertTrue(
            all(
                "trusting" not in personality.lower()
                for personality in observed_personalities
            )
        )


if __name__ == "__main__":
    unittest.main()
