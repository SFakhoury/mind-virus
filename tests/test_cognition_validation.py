import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from mind_virus.cognition_validation import (
    save_cognition_validation,
    validate_autonomous_cognition,
)


class CognitionValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.town, cls.report = validate_autonomous_cognition(days=3)

    def test_three_day_cognition_validation_passes(self):
        self.assertTrue(self.report.passed)

    def test_validation_observes_plans_conversations_and_reflections(self):
        self.assertGreaterEqual(self.report.daily_plans, 12)
        self.assertGreaterEqual(self.report.conversations, 1)
        self.assertGreaterEqual(self.report.reflections, 1)

    def test_validation_checks_traceable_lineage(self):
        self.assertTrue(self.report.conversation_lineage_valid)
        self.assertTrue(self.report.reflection_lineage_valid)

    def test_validation_report_is_saved(self):
        with TemporaryDirectory() as directory:
            output = save_cognition_validation(
                self.town,
                self.report,
                Path(directory) / "phase9.json",
            )
            saved = json.loads(output.read_text(encoding="utf-8"))

        self.assertTrue(saved["passed"])
        self.assertEqual(saved["report"]["simulated_days"], 3)

    def test_validation_rejects_zero_days(self):
        with self.assertRaises(ValueError):
            validate_autonomous_cognition(days=0)


if __name__ == "__main__":
    unittest.main()
