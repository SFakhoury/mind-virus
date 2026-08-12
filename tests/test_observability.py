import json
import logging
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from mind_virus.observability import JsonFormatter, OperationalMetrics, redact


class ObservabilityTests(unittest.TestCase):
    def test_sensitive_values_are_redacted_recursively(self):
        value = redact({"token": "secret", "nested": {"OPENAI_API_KEY": "key"}, "safe": 3})
        self.assertEqual(value, {"token": "[REDACTED]", "nested": {"OPENAI_API_KEY": "[REDACTED]"}, "safe": 3})

    def test_log_formatter_emits_json(self):
        record = logging.LogRecord("test", logging.INFO, "", 0, "request complete", (), None)
        record.context = {"status": 200, "authorization": "Bearer secret"}
        payload = json.loads(JsonFormatter().format(record))
        self.assertEqual(payload["context"]["authorization"], "[REDACTED]")
        self.assertEqual(payload["context"]["status"], 200)

    def test_metrics_count_events_and_report_uptime(self):
        metrics = OperationalMetrics()
        metrics.increment("requests_total")
        metrics.increment("requests_total")
        snapshot = metrics.snapshot()
        self.assertEqual(snapshot["counters"]["requests_total"], 2)
        self.assertGreaterEqual(snapshot["uptime_seconds"], 0)


if __name__ == "__main__":
    unittest.main()
