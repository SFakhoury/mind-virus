from __future__ import annotations

from collections.abc import Callable
from threading import Event, Thread


class WorldClock:
    """Advance a world from one server-owned background clock."""

    def __init__(
        self,
        advance: Callable[[], None],
        *,
        interval_seconds: float = 2.0,
    ) -> None:
        if interval_seconds <= 0:
            raise ValueError("Clock interval must be positive.")
        self._advance = advance
        self._interval_seconds = interval_seconds
        self._stop = Event()
        self._thread: Thread | None = None

    @property
    def running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def tick_once(self) -> None:
        self._advance()

    def start(self) -> None:
        if self.running:
            return
        self._stop.clear()
        self._thread = Thread(
            target=self._run,
            name="mind-virus-world-clock",
            daemon=True,
        )
        self._thread.start()

    def stop(self, timeout: float = 2.0) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout)

    def _run(self) -> None:
        while not self._stop.wait(self._interval_seconds):
            self.tick_once()
