from __future__ import annotations

from dataclasses import dataclass, asdict
import json
from pathlib import Path

from .world import WorldState, build_default_world


@dataclass(frozen=True)
class WorldValidationReport:
    simulated_days: int
    elapsed_minutes: int
    final_day: int
    events_recorded: int
    scheduled_events_triggered: int
    departures: int
    arrivals: int
    active_travelers: int
    needs_within_bounds: bool
    travel_state_valid: bool
    replay_identical: bool

    @property
    def passed(self) -> bool:
        return (
            self.needs_within_bounds
            and self.travel_state_valid
            and self.replay_identical
            and self.departures == self.arrivals + self.active_travelers
        )


def validate_world(days: int = 3) -> tuple[WorldState, WorldValidationReport]:
    if days < 1:
        raise ValueError("Validation must simulate at least one day.")
    elapsed_minutes = days * 1440
    world = build_default_world()
    world.tick(elapsed_minutes)

    replay = build_default_world()
    replay.tick(elapsed_minutes)
    event_types = [event["type"] for event in world.event_log]
    needs_valid = all(
        0.0 <= value <= 1.0
        for resident in world.residents.values()
        for value in (
            resident.needs.energy,
            resident.needs.hunger,
            resident.needs.social,
        )
    )
    travel_valid = all(
        resident.travel_remaining >= 0
        and (
            resident.destination_id is not None
            or resident.travel_remaining == 0
        )
        for resident in world.residents.values()
    )
    report = WorldValidationReport(
        simulated_days=days,
        elapsed_minutes=elapsed_minutes,
        final_day=world.day,
        events_recorded=len(world.event_log),
        scheduled_events_triggered=event_types.count("world_event"),
        departures=event_types.count("departure"),
        arrivals=event_types.count("arrival"),
        active_travelers=sum(
            resident.travel_remaining > 0
            for resident in world.residents.values()
        ),
        needs_within_bounds=needs_valid,
        travel_state_valid=travel_valid,
        replay_identical=replay.to_dict() == world.to_dict(),
    )
    return world, report


def save_validation(
    world: WorldState,
    report: WorldValidationReport,
    path: str | Path,
) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(
            {"report": asdict(report), "passed": report.passed, "world": world.to_dict()},
            indent=2,
        ),
        encoding="utf-8",
    )
    return output
