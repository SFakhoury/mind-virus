import unittest

from mind_virus.api_budget import (
    BudgetExceeded,
    BudgetLedger,
    BudgetPolicy,
    ModelPricing,
)


class APIBudgetTests(unittest.TestCase):
    def test_reservation_blocks_session_call_overrun(self):
        ledger = BudgetLedger(BudgetPolicy(max_session_calls=1))
        ledger.reserve("Alice", estimated_input_tokens=10, estimated_output_tokens=5)

        with self.assertRaises(BudgetExceeded):
            ledger.reserve("Bob", estimated_input_tokens=10, estimated_output_tokens=5)

    def test_reservation_blocks_per_agent_overrun(self):
        ledger = BudgetLedger(BudgetPolicy(max_agent_calls=1))
        reservation = ledger.reserve(
            "Alice", estimated_input_tokens=10, estimated_output_tokens=5
        )
        ledger.reconcile(
            reservation.id, actual_input_tokens=8, actual_output_tokens=4
        )

        with self.assertRaises(BudgetExceeded):
            ledger.reserve("Alice", estimated_input_tokens=10, estimated_output_tokens=5)

    def test_pending_reservations_count_against_cost_ceiling(self):
        policy = BudgetPolicy(
            max_session_cost_usd=0.001,
            pricing=ModelPricing(100.0, 100.0),
        )
        ledger = BudgetLedger(policy)
        ledger.reserve("Alice", estimated_input_tokens=5, estimated_output_tokens=0)

        with self.assertRaises(BudgetExceeded):
            ledger.reserve("Bob", estimated_input_tokens=6, estimated_output_tokens=0)

    def test_reconcile_records_actual_tokens_and_cost(self):
        ledger = BudgetLedger()
        reservation = ledger.reserve(
            "Alice", estimated_input_tokens=100, estimated_output_tokens=50
        )

        usage = ledger.reconcile(
            reservation.id, actual_input_tokens=80, actual_output_tokens=20
        )

        self.assertEqual(usage.calls, 1)
        self.assertEqual(usage.input_tokens, 80)
        self.assertEqual(ledger.session_usage.output_tokens, 20)
        self.assertGreater(usage.cost_usd, 0)

    def test_cancel_releases_reserved_capacity(self):
        ledger = BudgetLedger(BudgetPolicy(max_session_calls=1))
        reservation = ledger.reserve(
            "Alice", estimated_input_tokens=10, estimated_output_tokens=5
        )
        ledger.cancel(reservation.id)

        replacement = ledger.reserve(
            "Bob", estimated_input_tokens=10, estimated_output_tokens=5
        )

        self.assertEqual(replacement.agent_name, "Bob")

    def test_rate_limit_uses_rolling_minute(self):
        ledger = BudgetLedger(BudgetPolicy(max_calls_per_minute=1))
        ledger.reserve(
            "Alice", estimated_input_tokens=10, estimated_output_tokens=5, now=0
        )
        with self.assertRaises(BudgetExceeded):
            ledger.reserve(
                "Bob", estimated_input_tokens=10, estimated_output_tokens=5, now=30
            )

        reservation = ledger.reserve(
            "Bob", estimated_input_tokens=10, estimated_output_tokens=5, now=60
        )
        self.assertEqual(reservation.agent_name, "Bob")

    def test_ledger_round_trip_preserves_usage_and_reservations(self):
        ledger = BudgetLedger()
        first = ledger.reserve(
            "Alice", estimated_input_tokens=100, estimated_output_tokens=20, now=10
        )
        ledger.reconcile(first.id, actual_input_tokens=90, actual_output_tokens=10)
        ledger.reserve(
            "Bob", estimated_input_tokens=50, estimated_output_tokens=10, now=20
        )

        restored = BudgetLedger.from_dict(ledger.to_dict())

        self.assertEqual(restored.to_dict(), ledger.to_dict())

    def test_pricing_rejects_negative_values(self):
        with self.assertRaises(ValueError):
            ModelPricing(input_usd_per_million=-1)

    def test_actual_overrun_is_recorded_before_alert(self):
        ledger = BudgetLedger(
            BudgetPolicy(
                max_session_tokens=10,
                pricing=ModelPricing(0, 0),
            )
        )
        reservation = ledger.reserve(
            "Alice", estimated_input_tokens=5, estimated_output_tokens=0
        )

        with self.assertRaises(BudgetExceeded):
            ledger.reconcile(
                reservation.id,
                actual_input_tokens=11,
                actual_output_tokens=0,
            )

        self.assertEqual(ledger.session_usage.input_tokens, 11)
        self.assertEqual(ledger.session_usage.calls, 1)


if __name__ == "__main__":
    unittest.main()
