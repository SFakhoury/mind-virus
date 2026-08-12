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
                connection.execute("""
                    CREATE TABLE IF NOT EXISTS town_snapshots (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        mode TEXT NOT NULL,
                        payload TEXT NOT NULL
                    )
                """)
                connection.execute("""
                    CREATE TABLE IF NOT EXISTS current_town_state (
                        singleton INTEGER PRIMARY KEY CHECK (singleton = 1),
                        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        mode TEXT NOT NULL,
                        payload TEXT NOT NULL
                    )
                """)

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
        return {"status": "ok", "database": "ok"}
