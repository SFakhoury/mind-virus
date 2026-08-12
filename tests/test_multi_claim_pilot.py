import unittest

from mind_virus.calibrated_pilot import (
    run_calibrated_pilot,
)
from mind_virus.config import ExperimentConfig
from mind_virus.decision import TransmissionDecision
from mind_virus.seed_claims import SEED_CLAIMS


def mock_decision(listener, speaker, message):
    skeptical = (
        "corroborating evidence"
        in listener.personality
    )

    return TransmissionDecision(
        remembered_message=(
            f"{speaker.name} shared this report: {message}"
        ),
        believes_claim=not skeptical,
        repeats_claim=not skeptical,
        belief_confidence=0.2 if skeptical else 0.6,
        reason=(
            "No corroboration."
            if skeptical
            else "The report seems plausible."
        ),
    )


class MultiClaimPilotTests(unittest.TestCase):
    def test_runner_accepts_every_seed_claim(self) -> None:
        config = ExperimentConfig(
            trials_per_condition=1,
            agents_per_trial=3,
            maximum_api_calls=4,
        )

        for claim in SEED_CLAIMS:
            result = run_calibrated_pilot(
                config=config,
                decision_maker=mock_decision,
                original_message=claim.message,
            )

            first_records = [
                record
                for record in result.records
                if record.generation == 1
            ]

            self.assertTrue(
                all(
                    record.input_message
                    == claim.message
                    for record in first_records
                )
            )


if __name__ == "__main__":
    unittest.main()
