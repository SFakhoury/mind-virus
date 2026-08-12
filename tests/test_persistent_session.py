import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from mind_virus.persistent_session import PersistentSession


class PersistentSessionTests(unittest.TestCase):
    def test_tick_creates_atomic_checkpoint(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "session.json"
            session = PersistentSession.create(path)

            session.tick(20)

            self.assertTrue(path.is_file())
            self.assertFalse(path.with_suffix(".json.tmp").exists())
            self.assertEqual(json.loads(path.read_text())["schema_version"], 1)

    def test_load_restores_complete_session_state(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "session.json"
            original = PersistentSession.create(path)
            original.tick(20)
            restored = PersistentSession.load(path)

            self.assertEqual(restored.to_dict(), original.to_dict())

    def test_resume_does_not_duplicate_processed_interactions(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "session.json"
            original = PersistentSession.create(path)
            original.tick(20)
            count = len(original.town.conversations)
            restored = PersistentSession.load(path)

            restored.town.process_new_interactions()

            self.assertEqual(len(restored.town.conversations), count)

    def test_paused_session_cannot_advance_until_resumed(self):
        with TemporaryDirectory() as directory:
            session = PersistentSession.create(Path(directory) / "session.json")
            session.pause()

            with self.assertRaises(RuntimeError):
                session.tick()
            session.resume()
            session.tick()

    def test_load_rejects_unknown_schema(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "session.json"
            path.write_text('{"schema_version": 99}', encoding="utf-8")

            with self.assertRaises(ValueError):
                PersistentSession.load(path)

    def test_budget_usage_and_pending_reservations_survive_resume(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "session.json"
            session = PersistentSession.create(path)
            reservation = session.budget.reserve(
                "Alice", estimated_input_tokens=100, estimated_output_tokens=20
            )
            session.budget.reconcile(
                reservation.id,
                actual_input_tokens=80,
                actual_output_tokens=10,
            )
            session.budget.reserve(
                "Bob", estimated_input_tokens=50, estimated_output_tokens=10
            )
            session.save()

            restored = PersistentSession.load(path)

            self.assertEqual(restored.budget.to_dict(), session.budget.to_dict())

    def test_dialogue_rejection_log_survives_resume(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "session.json"
            session = PersistentSession.create(path)
            session.town.dialogue_rejections.append(
                {
                    "speaker": "Dana",
                    "listener": "Alice",
                    "reasons": ["message introduces unsupported named entities"],
                }
            )
            session.save()

            restored = PersistentSession.load(path)

            self.assertEqual(
                restored.town.dialogue_rejections,
                session.town.dialogue_rejections,
            )


if __name__ == "__main__":
    unittest.main()
