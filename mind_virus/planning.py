from __future__ import annotations

from dataclasses import dataclass

from mind_virus.agent import Agent
from mind_virus.world import Location, ResidentState


@dataclass(frozen=True)
class DailyPlan:
    resident_name: str
    day: int
    goal: str
    destination_id: str
    activity: str
    source: str
    source_memory_ids: tuple[str, ...]
    reason: str


def create_daily_plan(
    agent: Agent,
    resident: ResidentState,
    locations: dict[str, Location],
    day: int,
) -> DailyPlan:
    """Create one grounded daily goal from role, needs, and memories."""
    if day < 1:
        raise ValueError("Plan day must be at least one.")
    home_id = f"{resident.name.lower()}_home"
    needs = resident.needs
    if needs.energy <= 0.25:
        return _plan(
            resident, day, "recover energy", home_id, "resting", "energy",
            (), f"energy is critically low ({needs.energy:.2f})",
        )
    if needs.hunger >= 0.75:
        return _plan(
            resident, day, "find a meal", "bakery", "eating", "hunger",
            (), f"hunger is high ({needs.hunger:.2f})",
        )
    if needs.social >= 0.75:
        return _plan(
            resident, day, "meet another resident", "town_hall",
            "socializing", "social", (),
            f"social need is high ({needs.social:.2f})",
        )

    for memory in agent.memories.recent(limit=max(1, len(agent.memories))):
        destination = _mentioned_location(memory.content, locations)
        if destination is not None and not destination.endswith("_home"):
            activity = _memory_activity(agent.personality)
            return _plan(
                resident,
                day,
                f"follow up on a memory at {locations[destination].name}",
                destination,
                activity,
                "memory",
                (memory.id,),
                "a recent private memory identifies a relevant place",
            )

    destination, activity = _role_default(agent.personality, resident)
    return _plan(
        resident,
        day,
        f"carry out {activity} responsibilities",
        destination,
        activity,
        "role",
        (),
        "role and personality provide the default daily priority",
    )


def _plan(
    resident: ResidentState,
    day: int,
    goal: str,
    destination: str,
    activity: str,
    source: str,
    memory_ids: tuple[str, ...],
    reason: str,
) -> DailyPlan:
    return DailyPlan(
        resident.name,
        day,
        goal,
        destination,
        activity,
        source,
        memory_ids,
        reason,
    )


def _mentioned_location(
    content: str,
    locations: dict[str, Location],
) -> str | None:
    lowered = content.casefold()
    matches = [
        location_id for location_id, location in locations.items()
        if location.name.casefold() in lowered
        or location_id.replace("_", " ") in lowered
    ]
    return sorted(matches)[0] if matches else None


def _memory_activity(personality: str) -> str:
    lowered = personality.casefold()
    if "reporter" in lowered:
        return "investigating"
    if "baker" in lowered or "bakery" in lowered:
        return "checking supplies"
    if "librarian" in lowered:
        return "researching"
    if "planner" in lowered:
        return "planning visit"
    return "following up"


def _role_default(
    personality: str,
    resident: ResidentState,
) -> tuple[str, str]:
    lowered = personality.casefold()
    if "reporter" in lowered:
        return "town_hall", "reporting"
    if "baker" in lowered or "bakery" in lowered:
        return "bakery", "working"
    if "librarian" in lowered:
        return "library", "working"
    if "planner" in lowered:
        return "town_hall", "planning"
    entry = resident.next_schedule_entry(720)
    return entry.location_id, entry.activity
