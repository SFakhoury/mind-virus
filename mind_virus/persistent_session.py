from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path
from uuid import uuid4

from mind_virus.agent import Agent
from mind_virus.api_budget import BudgetLedger
from mind_virus.autonomous_town import (
    AutonomousConversation,
    AutonomousReflection,
    AutonomousTown,
)
from mind_virus.belief import Belief
from mind_virus.memory import Memory
from mind_virus.planning import DailyPlan
from mind_virus.world import WorldState


@dataclass
class PersistentSession:
    """A resumable autonomous town with one atomic checkpoint."""

    town: AutonomousTown
    checkpoint_path: Path
    session_id: str
    created_at: str
    updated_at: str
    status: str = "running"
    budget: BudgetLedger = field(default_factory=BudgetLedger)

    @classmethod
    def create(
        cls,
        checkpoint_path: str | Path,
        *,
        town: AutonomousTown | None = None,
    ) -> "PersistentSession":
        now = _utc_now()
        return cls(
            town=town if town is not None else AutonomousTown(),
            checkpoint_path=Path(checkpoint_path),
            session_id=str(uuid4()),
            created_at=now,
            updated_at=now,
        )

    def tick(self, minutes: int = 1) -> None:
        if self.status != "running":
            raise RuntimeError("Only a running session can advance.")
        self.town.tick(minutes)
        self.save()

    def pause(self) -> None:
        self.status = "paused"
        self.save()

    def resume(self) -> None:
        if self.status != "paused":
            raise RuntimeError("Only a paused session can resume.")
        self.status = "running"
        self.save()

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": 1,
            "session_id": self.session_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "status": self.status,
            "budget": self.budget.to_dict(),
            "event_cursor": self.town._event_cursor,
            "world": self.town.world.to_dict(),
            "agents": {
                name: {
                    "name": agent.name,
                    "personality": agent.personality,
                    "memories": [
                        {
                            **asdict(memory),
                            "created_at": memory.created_at.isoformat(),
                        }
                        for memory in agent.memories.all()
                    ],
                    "beliefs": [asdict(belief) for belief in agent._beliefs.values()],
                }
                for name, agent in self.town.agents.items()
            },
            "conversations": [
                asdict(item) for item in self.town.conversations
            ],
            "reflections": [asdict(item) for item in self.town.reflections],
            "daily_plans": [asdict(item) for item in self.town.daily_plans],
            "dialogue_rejections": list(self.town.dialogue_rejections),
        }

    def save(self) -> Path:
        self.updated_at = _utc_now()
        output = self.checkpoint_path
        output.parent.mkdir(parents=True, exist_ok=True)
        temporary = output.with_suffix(output.suffix + ".tmp")
        temporary.write_text(
            json.dumps(self.to_dict(), indent=2),
            encoding="utf-8",
        )
        temporary.replace(output)
        return output

    @classmethod
    def load(cls, checkpoint_path: str | Path) -> "PersistentSession":
        path = Path(checkpoint_path)
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("schema_version") != 1:
            raise ValueError("Unsupported persistent-session schema version.")
        agents: dict[str, Agent] = {}
        for name, raw_agent in data["agents"].items():
            agent = Agent(raw_agent["name"], raw_agent["personality"])
            for raw_memory in raw_agent["memories"]:
                memory_data = dict(raw_memory)
                memory_data["created_at"] = datetime.fromisoformat(
                    memory_data["created_at"]
                )
                memory_data["related_memory_ids"] = tuple(
                    memory_data.get("related_memory_ids", ())
                )
                agent.memories.add(Memory(**memory_data))
            for raw_belief in raw_agent["beliefs"]:
                belief = Belief(**raw_belief)
                agent._beliefs[belief.topic_id] = belief
            agents[name] = agent

        town = AutonomousTown(
            world=WorldState.from_dict(data["world"]),
            agents=agents,
        )
        town.conversations = [
            AutonomousConversation(
                **_tuple_fields(
                    item,
                    "topic_source_memory_ids",
                    "supporting_memory_ids",
                    "listener_relevant_memory_ids",
                )
            )
            for item in data.get("conversations", [])
        ]
        town.reflections = [
            AutonomousReflection(
                **_tuple_fields(item, "source_memory_ids")
            )
            for item in data.get("reflections", [])
        ]
        town.daily_plans = [
            DailyPlan(**_tuple_fields(item, "source_memory_ids"))
            for item in data.get("daily_plans", [])
        ]
        town.dialogue_rejections = list(data.get("dialogue_rejections", []))
        town._event_cursor = int(data.get("event_cursor", 0))
        return cls(
            town=town,
            checkpoint_path=path,
            session_id=data["session_id"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            status=data["status"],
            budget=BudgetLedger.from_dict(
                data.get("budget", BudgetLedger().to_dict())
            ),
        )


def _tuple_fields(data: dict[str, object], *fields: str) -> dict[str, object]:
    restored = dict(data)
    for field in fields:
        restored[field] = tuple(restored.get(field, ()))
    return restored


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
