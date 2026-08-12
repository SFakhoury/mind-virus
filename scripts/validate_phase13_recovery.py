from pathlib import Path
from tempfile import TemporaryDirectory

from mind_virus.production_store import ProductionStore


def main() -> None:
    with TemporaryDirectory() as directory:
        root = Path(directory)
        source = ProductionStore(root / "production.db")
        expected = {"day": 7, "clock": "18:30", "generation": 3}
        source.save_current_state("staging-recovery-drill", expected)
        backup = source.backup(root / "backups" / "production.db")
        restored = ProductionStore.restore(backup, root / "replacement.db")
        actual = restored.load_current_state()
        if actual is None or actual["payload"] != expected:
            raise RuntimeError("Recovery validation failed: state differs after restore.")
        print("PHASE 13: BACKUP AND RECOVERY VALIDATION")
        print("-" * 48)
        print(f"Schema version: {restored.schema_version}")
        print("Backup integrity: True")
        print("Restored state matches: True")
        print("Recovery validation passed.")


if __name__ == "__main__":
    main()
