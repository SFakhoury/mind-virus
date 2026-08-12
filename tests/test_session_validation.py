from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from mind_virus.session_validation import save_validation, validate_persistent_session


class PersistentSessionValidationTests(unittest.TestCase):
    def test_checkpoint_reload_and_continuation_pass(self):
        with TemporaryDirectory() as directory:
            validation = validate_persistent_session(
                Path(directory) / "session.json"
            )

            self.assertTrue(validation.passed)
            self.assertEqual(
                validation.minute_after_resume,
                validation.minute_before_resume + 5,
            )

    def test_validation_report_is_saved_as_json(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            validation = validate_persistent_session(root / "session.json")
            output = save_validation(validation, root / "validation.json")

            saved = json.loads(output.read_text(encoding="utf-8"))
            self.assertTrue(saved["passed"])
            self.assertTrue(saved["no_duplicate_conversations"])

    def test_validation_rejects_nonpositive_duration(self):
        with TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                validate_persistent_session(
                    Path(directory) / "session.json",
                    initial_minutes=0,
                )


if __name__ == "__main__":
    unittest.main()
