from threading import Thread
import time
import unittest

from mind_virus.live_sync import LiveStateBroker


class LiveStateBrokerTests(unittest.TestCase):
    def test_waiter_receives_new_revision_and_payload(self):
        broker = LiveStateBroker()
        received = []
        waiter = Thread(target=lambda: received.append(broker.wait_for_update(0, 1)))
        waiter.start()
        time.sleep(0.01)
        revision = broker.publish({"generation": 2})
        waiter.join()
        self.assertEqual(revision, 1)
        self.assertEqual(received, [(1, {"generation": 2})])

    def test_timeout_returns_current_revision(self):
        broker = LiveStateBroker()
        self.assertEqual(broker.wait_for_update(0, 0), (0, None))


if __name__ == "__main__":
    unittest.main()
