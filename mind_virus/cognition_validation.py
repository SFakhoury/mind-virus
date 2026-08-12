from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path

from mind_virus.autonomous_town import AutonomousTown


@dataclass(frozen=True)
class CognitionValidationReport:
    simulated_days: int
    elapsed_minutes: int
    daily_plans: int
    plan_sources: tuple[str, ...]
    decision_sources: tuple[str, ...]
    conversations: int
    reflections: int
    memories: int
    beliefs: int
    needs_within_bounds: bool
    relationships_within_bounds: bool
    routes_valid: bool
    conversation_lineage_valid: bool
    reflection_lineage_valid: bool
    decisions_separated: bool

    @property
    def passed(self) -> bool:
        return (
            self.daily_plans >= self.simulated_days * 4
            and len(self.plan_sources) >= 2
            and len(self.decision_sources) >= 2
            and self.conversations >= 1
            and self.reflections >= 1
            and self.needs_within_bounds
            and self.relationships_within_bounds
            and self.routes_valid
            and self.conversation_lineage_valid
            and self.reflection_lineage_valid
            and self.decisions_separated
        )


def validate_autonomous_cognition(
    days: int = 3,
) -> tuple[AutonomousTown, CognitionValidationReport]:
    if days < 1:
        raise ValueError("Validation must simulate at least one day.")
    town = AutonomousTown()
    elapsed_minutes = days * 1440
    decision_sources: set[str] = set()
    for _ in range(elapsed_minutes):
        town.tick()
        decision_sources.update(
            resident.decision_source
            for resident in town.world.residents.values()
        )

    memory_ids = {
        memory.id
        for agent in town.agents.values()
        for memory in agent.memories.all()
    }
    routes = {
        frozenset((route.start, route.end)) for route in town.world.routes
    }
    departure_routes_valid = all(
        event.get("type") != "departure"
        or frozenset((event["location"], event["destination"])) in routes
        for event in town.world.event_log
    )
    conversation_lineage_valid = all(
        conversation.speaker_memory_id in memory_ids
        and conversation.listener_memory_id in memory_ids
        and set(conversation.supporting_memory_ids).issubset(memory_ids)
        and set(conversation.topic_source_memory_ids).issubset(memory_ids)
        and set(conversation.listener_relevant_memory_ids).issubset(memory_ids)
        for conversation in town.conversations
    )
    reflection_lineage_valid = all(
        reflection.memory_id in memory_ids
        and len(reflection.source_memory_ids) >= 3
        and set(reflection.source_memory_ids).issubset(memory_ids)
        for reflection in town.reflections
    )
    report = CognitionValidationReport(
        simulated_days=days,
        elapsed_minutes=elapsed_minutes,
        daily_plans=len(town.daily_plans),
        plan_sources=tuple(sorted({plan.source for plan in town.daily_plans})),
        decision_sources=tuple(sorted(decision_sources)),
        conversations=len(town.conversations),
        reflections=len(town.reflections),
        memories=sum(len(agent.memories) for agent in town.agents.values()),
        beliefs=sum(len(agent._beliefs) for agent in town.agents.values()),
        needs_within_bounds=all(
            0.0 <= value <= 1.0
            for resident in town.world.residents.values()
            for value in (
                resident.needs.energy,
                resident.needs.hunger,
                resident.needs.social,
            )
        ),
        relationships_within_bounds=all(
            0.0 <= strength <= 1.0
            for resident in town.world.residents.values()
            for strength in resident.relationships.values()
        ),
        routes_valid=departure_routes_valid,
        conversation_lineage_valid=conversation_lineage_valid,
        reflection_lineage_valid=reflection_lineage_valid,
        decisions_separated=all(
            isinstance(conversation.listener_believes, bool)
            and isinstance(conversation.listener_repeats, bool)
            and 0.0 <= conversation.listener_confidence <= 1.0
            for conversation in town.conversations
        ),
    )
    return town, report


def save_cognition_validation(
    town: AutonomousTown,
    report: CognitionValidationReport,
    path: str | Path,
) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(
            {
                "report": asdict(report),
                "passed": report.passed,
                "world": town.world.to_dict(),
                "browser_state": town.browser_state(),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return output
