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


if __name__ == "__main__":
    unittest.main()
