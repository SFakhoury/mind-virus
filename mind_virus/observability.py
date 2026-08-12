from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import json
import logging
from pathlib import Path
from threading import Lock
import time
from typing import Any


SENSITIVE_KEYS = {"authorization", "openai_api_key", "mind_virus_access_token", "token"}


def redact(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: "[REDACTED]" if key.lower() in SENSITIVE_KEYS else redact(item)
                for key, item in value.items()}
    if isinstance(value, list):
        return [redact(item) for item in value]
    return value


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {"timestamp": datetime.now(timezone.utc).isoformat(),
                   "level": record.levelname, "message": record.getMessage()}
        if hasattr(record, "context"):
            payload["context"] = redact(record.context)
        return json.dumps(payload, sort_keys=True)


def production_logger(path: str | Path) -> logging.Logger:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(f"mind-virus.{output.resolve()}")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = logging.FileHandler(output, encoding="utf-8")
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
    return logger


class OperationalMetrics:
    def __init__(self) -> None:
        self.started_at = time.monotonic()
        self._counts: Counter[str] = Counter()
        self._lock = Lock()

    def increment(self, name: str) -> None:
        with self._lock:
            self._counts[name] += 1

    def snapshot(self) -> dict[str, object]:
        with self._lock:
            counts = dict(self._counts)
        return {"uptime_seconds": round(time.monotonic() - self.started_at, 3),
                "counters": counts}
