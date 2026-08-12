from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from mind_virus.production_store import ProductionStore
from scripts.run_town_ui import API_VERSION


class ProductionStoreTests(unittest.TestCase):
    def test_sqlite_snapshot_survives_new_store_instance(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "town.db"
            first = ProductionStore(path)
            snapshot_id = first.save_snapshot("simulation", {"day": 2})
            saved = ProductionStore(path).latest_snapshot()
            self.assertEqual(saved["id"], snapshot_id)
            self.assertEqual(saved["payload"], {"day": 2})

    def test_health_checks_database(self):
        with TemporaryDirectory() as directory:
            health = ProductionStore(Path(directory) / "town.db").health()
            self.assertEqual(health, {"status": "ok", "database": "ok"})

    def test_api_is_versioned(self):
        self.assertEqual(API_VERSION, "v1")

    def test_current_state_survives_restart_and_is_replaced_atomically(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "town.db"
            first = ProductionStore(path)
            first.save_current_state("simulation", {"generation": 1})
            first.save_current_state("simulation", {"generation": 2})

            restored = ProductionStore(path).load_current_state()

            self.assertEqual(restored["mode"], "simulation")
            self.assertEqual(restored["payload"], {"generation": 2})


if __name__ == "__main__":
    unittest.main()
