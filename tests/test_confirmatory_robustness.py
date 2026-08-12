from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock
import json
import unittest

from mind_virus.confirmatory_robustness import (
    ConfirmatoryRobustnessProtocol, collect_confirmatory_robustness,
)


class ConfirmatoryRobustnessTests(unittest.TestCase):
    def test_protocol_contains_approved_powered_design(self):
        protocol = ConfirmatoryRobustnessProtocol()
        self.assertEqual(protocol.planned_calls, 648)
        self.assertEqual(protocol.plan.base.trials_per_cell, 27)
        self.assertLess(protocol.plan.estimated_cost_usd, 1.50)

    def test_protocol_fingerprint_is_stable(self):
        self.assertEqual(
            ConfirmatoryRobustnessProtocol().fingerprint,
            ConfirmatoryRobustnessProtocol().fingerprint,
        )

    def test_protocol_freeze_is_idempotent(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "protocol.json"
            first = ConfirmatoryRobustnessProtocol().freeze(path)
            second = ConfirmatoryRobustnessProtocol().freeze(path)
            self.assertEqual(first, second)

    def test_changed_frozen_protocol_is_rejected(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "protocol.json"
            ConfirmatoryRobustnessProtocol().freeze(path)
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["alpha"] = 0.10
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(FileExistsError):
                ConfirmatoryRobustnessProtocol().freeze(path)

    def test_collection_rejects_nonmatching_protocol_before_api_calls(self):
        client = Mock()
        with TemporaryDirectory() as directory:
            protocol_path = Path(directory) / "protocol.json"
            protocol_path.write_text('{"fingerprint": "wrong"}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "does not match"):
                collect_confirmatory_robustness(
                    ConfirmatoryRobustnessProtocol(), protocol_path,
                    Path(directory) / "results.json", client=client,
                )
        client.responses.parse.assert_not_called()


if __name__ == "__main__":
    unittest.main()
