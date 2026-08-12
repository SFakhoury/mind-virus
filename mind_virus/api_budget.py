from __future__ import annotations

from dataclasses import asdict, dataclass, field
import time
from uuid import uuid4


class BudgetExceeded(RuntimeError):
    """Raised before a model request that would exceed a local safeguard."""


@dataclass(frozen=True)
class ModelPricing:
    input_usd_per_million: float = 0.20
    output_usd_per_million: float = 1.20

    def __post_init__(self) -> None:
        if self.input_usd_per_million < 0 or self.output_usd_per_million < 0:
            raise ValueError("Model prices cannot be negative.")

    def estimate(self, input_tokens: int, output_tokens: int) -> float:
        return (
            input_tokens * self.input_usd_per_million
            + output_tokens * self.output_usd_per_million
        ) / 1_000_000


@dataclass(frozen=True)
class BudgetPolicy:
    max_session_calls: int = 100
    max_agent_calls: int = 30
    max_session_tokens: int = 1_000_000
    max_session_cost_usd: float = 0.50
    max_calls_per_minute: int = 10
    pricing: ModelPricing = field(default_factory=ModelPricing)

    def __post_init__(self) -> None:
        if min(
            self.max_session_calls,
            self.max_agent_calls,
            self.max_session_tokens,
            self.max_calls_per_minute,
        ) < 1:
            raise ValueError("Budget call and token limits must be positive.")
        if self.max_session_cost_usd <= 0:
            raise ValueError("Session cost limit must be positive.")


@dataclass
class AgentUsage:
    calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0


@dataclass(frozen=True)
class BudgetReservation:
    id: str
    agent_name: str
    estimated_input_tokens: int
    estimated_output_tokens: int
    estimated_cost_usd: float
    created_at: float


class BudgetLedger:
    """Reserve and reconcile local model-call budgets before API requests."""

    def __init__(self, policy: BudgetPolicy | None = None) -> None:
        self.policy = policy or BudgetPolicy()
        self.session_usage = AgentUsage()
        self.agent_usage: dict[str, AgentUsage] = {}
        self.reservations: dict[str, BudgetReservation] = {}
        self.call_timestamps: list[float] = []

    def reserve(
        self,
        agent_name: str,
        *,
        estimated_input_tokens: int,
        estimated_output_tokens: int,
        now: float | None = None,
    ) -> BudgetReservation:
        if not agent_name.strip():
            raise ValueError("Budget reservation requires an agent name.")
        if estimated_input_tokens < 0 or estimated_output_tokens < 0:
            raise ValueError("Estimated tokens cannot be negative.")
        timestamp = time.time() if now is None else now
        self.call_timestamps = [
            value for value in self.call_timestamps
            if timestamp - value < 60
        ]
        if len(self.call_timestamps) >= self.policy.max_calls_per_minute:
            raise BudgetExceeded("Session request rate limit reached.")

        pending = list(self.reservations.values())
        pending_calls = len(pending)
        agent_pending = sum(item.agent_name == agent_name for item in pending)
        usage = self.agent_usage.get(agent_name, AgentUsage())
        estimated_cost = self.policy.pricing.estimate(
            estimated_input_tokens,
            estimated_output_tokens,
        )
        pending_tokens = sum(
            item.estimated_input_tokens + item.estimated_output_tokens
            for item in pending
        )
        pending_cost = sum(item.estimated_cost_usd for item in pending)
        checks = (
            (
                self.session_usage.calls + pending_calls + 1
                <= self.policy.max_session_calls,
                "Session call budget exhausted.",
            ),
            (
                usage.calls + agent_pending + 1 <= self.policy.max_agent_calls,
                f"Agent call budget exhausted for {agent_name}.",
            ),
            (
                self.session_usage.input_tokens
                + self.session_usage.output_tokens
                + pending_tokens
                + estimated_input_tokens
                + estimated_output_tokens
                <= self.policy.max_session_tokens,
                "Session token budget exhausted.",
            ),
            (
                self.session_usage.cost_usd + pending_cost + estimated_cost
                <= self.policy.max_session_cost_usd,
                "Session cost budget exhausted.",
            ),
        )
        for allowed, message in checks:
            if not allowed:
                raise BudgetExceeded(message)

        reservation = BudgetReservation(
            id=str(uuid4()),
            agent_name=agent_name,
            estimated_input_tokens=estimated_input_tokens,
            estimated_output_tokens=estimated_output_tokens,
            estimated_cost_usd=estimated_cost,
            created_at=timestamp,
        )
        self.reservations[reservation.id] = reservation
        self.call_timestamps.append(timestamp)
        return reservation

    def reconcile(
        self,
        reservation_id: str,
        *,
        actual_input_tokens: int,
        actual_output_tokens: int,
    ) -> AgentUsage:
        if actual_input_tokens < 0 or actual_output_tokens < 0:
            raise ValueError("Actual tokens cannot be negative.")
        try:
            reservation = self.reservations[reservation_id]
        except KeyError as error:
            raise ValueError("Unknown budget reservation.") from error
        cost = self.policy.pricing.estimate(
            actual_input_tokens,
            actual_output_tokens,
        )
        cost_exceeded = (
            self.session_usage.cost_usd + cost
            > self.policy.max_session_cost_usd
        )
        tokens_exceeded = (
            self.session_usage.input_tokens
            + self.session_usage.output_tokens
            + actual_input_tokens
            + actual_output_tokens
            > self.policy.max_session_tokens
        )
        self.reservations.pop(reservation_id)
        agent = self.agent_usage.setdefault(reservation.agent_name, AgentUsage())
        for usage in (self.session_usage, agent):
            usage.calls += 1
            usage.input_tokens += actual_input_tokens
            usage.output_tokens += actual_output_tokens
            usage.cost_usd += cost
        if cost_exceeded:
            raise BudgetExceeded("Actual usage exceeded the session cost ceiling.")
        if tokens_exceeded:
            raise BudgetExceeded("Actual usage exceeded the session token ceiling.")
        return agent

    def cancel(self, reservation_id: str) -> None:
        if self.reservations.pop(reservation_id, None) is None:
            raise ValueError("Unknown budget reservation.")

    def to_dict(self) -> dict[str, object]:
        return {
            "policy": {
                **asdict(self.policy),
                "pricing": asdict(self.policy.pricing),
            },
            "session_usage": asdict(self.session_usage),
            "agent_usage": {
                name: asdict(usage) for name, usage in self.agent_usage.items()
            },
            "reservations": {
                key: asdict(value) for key, value in self.reservations.items()
            },
            "call_timestamps": list(self.call_timestamps),
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "BudgetLedger":
        raw_policy = dict(data["policy"])
        raw_policy["pricing"] = ModelPricing(**raw_policy["pricing"])
        ledger = cls(BudgetPolicy(**raw_policy))
        ledger.session_usage = AgentUsage(**data["session_usage"])
        ledger.agent_usage = {
            name: AgentUsage(**usage)
            for name, usage in data.get("agent_usage", {}).items()
        }
        ledger.reservations = {
            key: BudgetReservation(**reservation)
            for key, reservation in data.get("reservations", {}).items()
        }
        ledger.call_timestamps = list(data.get("call_timestamps", []))
        return ledger
