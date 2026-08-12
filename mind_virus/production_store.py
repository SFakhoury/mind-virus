from __future__ import annotations

import json
from contextlib import closing
from pathlib import Path
import sqlite3
from typing import Any


class ProductionStore:
    """Small durable SQLite foundation for production town snapshots."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with closing(self._connect()) as connection:
            with connection:
                version = int(connection.execute("PRAGMA user_version").fetchone()[0])
                if version < 1:
                    connection.execute("""
                    CREATE TABLE IF NOT EXISTS town_snapshots (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        mode TEXT NOT NULL,
                        payload TEXT NOT NULL
                    )
                    """)
                    connection.execute("PRAGMA user_version = 1")
                if version < 2:
                    connection.execute("""
                    CREATE TABLE IF NOT EXISTS current_town_state (
                        singleton INTEGER PRIMARY KEY CHECK (singleton = 1),
                        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        mode TEXT NOT NULL,
                        payload TEXT NOT NULL
                    )
                    """)
                    connection.execute("PRAGMA user_version = 2")

    @property
    def schema_version(self) -> int:
        with closing(self._connect()) as connection:
            return int(connection.execute("PRAGMA user_version").fetchone()[0])

    def backup(self, destination: str | Path) -> Path:
        output = Path(destination)
        output.parent.mkdir(parents=True, exist_ok=True)
        with closing(self._connect()) as source, closing(sqlite3.connect(output)) as target:
            source.backup(target)
        return output

    @classmethod
    def restore(cls, backup_path: str | Path, destination: str | Path) -> "ProductionStore":
        source_path = Path(backup_path)
        if not source_path.is_file():
            raise FileNotFoundError(source_path)
        output = Path(destination)
        output.parent.mkdir(parents=True, exist_ok=True)
        with closing(sqlite3.connect(source_path)) as source, closing(sqlite3.connect(output)) as target:
            source.backup(target)
        restored = cls(output)
        if restored.health()["status"] != "ok":
            raise RuntimeError("Restored database failed its health check.")
        return restored

    def save_snapshot(self, mode: str, payload: dict[str, Any]) -> int:
        with closing(self._connect()) as connection:
            with connection:
                cursor = connection.execute(
                    "INSERT INTO town_snapshots (mode, payload) VALUES (?, ?)",
                    (mode, json.dumps(payload, sort_keys=True)),
                )
                return int(cursor.lastrowid)

    def latest_snapshot(self) -> dict[str, Any] | None:
        with closing(self._connect()) as connection:
            row = connection.execute(
                "SELECT id, created_at, mode, payload FROM town_snapshots ORDER BY id DESC LIMIT 1"
            ).fetchone()
        if row is None:
            return None
        return {"id": row["id"], "created_at": row["created_at"],
                "mode": row["mode"], "payload": json.loads(row["payload"])}

    def save_current_state(self, mode: str, payload: dict[str, Any]) -> None:
        """Atomically replace the one restart-safe current town snapshot."""
        encoded = json.dumps(payload, sort_keys=True)
        with closing(self._connect()) as connection:
            with connection:
                connection.execute("""
                    INSERT INTO current_town_state (singleton, mode, payload)
                    VALUES (1, ?, ?)
                    ON CONFLICT(singleton) DO UPDATE SET
                        updated_at = CURRENT_TIMESTAMP,
                        mode = excluded.mode,
                        payload = excluded.payload
                """, (mode, encoded))

    def load_current_state(self) -> dict[str, Any] | None:
        with closing(self._connect()) as connection:
            row = connection.execute(
                "SELECT updated_at, mode, payload FROM current_town_state WHERE singleton = 1"
            ).fetchone()
        if row is None:
            return None
        return {"updated_at": row["updated_at"], "mode": row["mode"],
                "payload": json.loads(row["payload"])}

    def health(self) -> dict[str, object]:
        with closing(self._connect()) as connection:
            connection.execute("SELECT 1").fetchone()
        return {"status": "ok", "database": "ok", "schema_version": self.schema_version}
