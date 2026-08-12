from __future__ import annotations

from threading import Condition
from typing import Any


class LiveStateBroker:
    """Thread-safe latest-state broadcaster for browser event streams."""

    def __init__(self) -> None:
        self._condition = Condition()
        self._revision = 0
        self._payload: dict[str, Any] | None = None

    def publish(self, payload: dict[str, Any]) -> int:
        with self._condition:
            self._revision += 1
            self._payload = payload
            self._condition.notify_all()
            return self._revision

    def wait_for_update(self, after_revision: int, timeout: float = 15.0):
        with self._condition:
            self._condition.wait_for(
                lambda: self._revision > after_revision, timeout=timeout
            )
            return self._revision, self._payload
