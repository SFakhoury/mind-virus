from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass
from threading import BoundedSemaphore, Lock
import time
from typing import Any, Callable
from uuid import uuid4


@dataclass
class JobRecord:
    id: str
    status: str = "queued"
    attempts: int = 0
    result: Any = None
    error: str | None = None


class BackgroundJobQueue:
    """Bounded in-process job runner with retry and observable status."""

    def __init__(self, *, max_workers: int = 2, max_pending: int = 16,
                 max_retries: int = 2, retry_delay: float = 0.05) -> None:
        self._executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="mind-virus")
        self._capacity = BoundedSemaphore(max_pending)
        self._max_retries = max_retries
        self._retry_delay = retry_delay
        self._jobs: dict[str, JobRecord] = {}
        self._lock = Lock()

    def submit(self, operation: Callable[[], Any]) -> str:
        if not self._capacity.acquire(blocking=False):
            raise RuntimeError("Background job queue is full.")
        job = JobRecord(str(uuid4()))
        with self._lock:
            self._jobs[job.id] = job
        self._executor.submit(self._run, job, operation)
        return job.id

    def _run(self, job: JobRecord, operation: Callable[[], Any]) -> None:
        try:
            for attempt in range(1, self._max_retries + 2):
                with self._lock:
                    job.status = "running"
                    job.attempts = attempt
                try:
                    result = operation()
                except Exception as error:
                    if attempt > self._max_retries:
                        with self._lock:
                            job.status = "failed"
                            job.error = str(error)
                        return
                    time.sleep(self._retry_delay * attempt)
                else:
                    with self._lock:
                        job.status = "completed"
                        job.result = result
                    return
        finally:
            self._capacity.release()

    def status(self, job_id: str) -> dict[str, Any] | None:
        with self._lock:
            job = self._jobs.get(job_id)
            return asdict(job) if job else None

    def metrics(self) -> dict[str, int]:
        with self._lock:
            values = list(self._jobs.values())
        return {state: sum(job.status == state for job in values)
                for state in ("queued", "running", "completed", "failed")}

    def shutdown(self) -> None:
        self._executor.shutdown(wait=True)
