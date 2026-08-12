import time
import unittest

from mind_virus.background_jobs import BackgroundJobQueue


def wait(queue, job_id):
    for _ in range(200):
        status = queue.status(job_id)
        if status["status"] in ("completed", "failed"):
            return status
        time.sleep(0.005)
    raise AssertionError("Job did not finish.")


class BackgroundJobQueueTests(unittest.TestCase):
    def test_completed_result_is_observable(self):
        queue = BackgroundJobQueue(retry_delay=0)
        try:
            status = wait(queue, queue.submit(lambda: {"generation": 2}))
            self.assertEqual(status["status"], "completed")
            self.assertEqual(status["result"], {"generation": 2})
        finally:
            queue.shutdown()

    def test_transient_failure_is_retried(self):
        queue = BackgroundJobQueue(max_retries=2, retry_delay=0)
        attempts = []
        def operation():
            attempts.append(1)
            if len(attempts) < 2:
                raise RuntimeError("temporary")
            return "ok"
        try:
            status = wait(queue, queue.submit(operation))
            self.assertEqual((status["status"], status["attempts"]), ("completed", 2))
        finally:
            queue.shutdown()

    def test_permanent_failure_is_recorded(self):
        queue = BackgroundJobQueue(max_retries=1, retry_delay=0)
        try:
            status = wait(queue, queue.submit(lambda: (_ for _ in ()).throw(RuntimeError("bad"))))
            self.assertEqual(status["status"], "failed")
            self.assertEqual(status["attempts"], 2)
        finally:
            queue.shutdown()


if __name__ == "__main__":
    unittest.main()
