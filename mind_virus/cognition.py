from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from mind_virus.world import ResidentState, ScheduleEntry


DecisionSource = Literal["schedule", "goal", "energy", "hunger", "social"]


@dataclass(frozen=True)
class ResidentDecision:
    """A traceable action selected from a resident's schedule and needs."""

    activity: str
    destination_id: str
    source: DecisionSource
    urgency: float
    reason: str


def choose_resident_action(
    resident: ResidentState,
    minute_of_day: int,
) -> ResidentDecision:
    """Choose the resident's most urgent action without mutating the world."""
    if not 0 <= minute_of_day < 1440:
        raise ValueError("Decision minute must be within one day.")

    scheduled = resident.next_schedule_entry(minute_of_day)
    needs = resident.needs
    candidates = (
        (
            1.0 - needs.energy,
            0.75,
            "resting",
            _home_id(resident),
            "energy",
            f"energy is low ({needs.energy:.2f})",
        ),
        (
            needs.hunger,
            0.70,
            "eating",
            "bakery",
            "hunger",
            f"hunger is high ({needs.hunger:.2f})",
        ),
        (
            needs.social,
            0.75,
            "socializing",
            "town_hall",
            "social",
            f"social need is high ({needs.social:.2f})",
        ),
    )
    urgent = [candidate for candidate in candidates if candidate[0] >= candidate[1]]
    if urgent:
        score, _, activity, destination, source, reason = max(
            urgent,
            key=lambda candidate: candidate[0],
        )
        return ResidentDecision(
            activity=activity,
            destination_id=destination,
            source=source,
            urgency=score,
            reason=reason,
        )

    if (
        420 <= minute_of_day < 1020
        and resident.goal_destination_id is not None
        and resident.goal_activity is not None
    ):
        return ResidentDecision(
            activity=resident.goal_activity,
            destination_id=resident.goal_destination_id,
            source="goal",
            urgency=0.25,
            reason=resident.goal_reason or resident.daily_goal,
        )

    return _scheduled_decision(scheduled)


def choose_conversation_partner(
    resident: ResidentState,
    candidates: list[ResidentState],
) -> ResidentState | None:
    """Select a co-located partner when the resident needs social contact."""
    if resident.needs.social < 0.75:
        return None
    eligible = [
        candidate
        for candidate in candidates
        if candidate.name != resident.name
        and candidate.location_id == resident.location_id
        and candidate.travel_remaining == 0
    ]
    if not eligible:
        return None
    return max(
        eligible,
        key=lambda candidate: (
            resident.relationships.get(candidate.name, 0.5),
            candidate.needs.social,
            candidate.name,
        ),
    )


def _scheduled_decision(entry: ScheduleEntry) -> ResidentDecision:
    return ResidentDecision(
        activity=entry.activity,
        destination_id=entry.location_id,
        source="schedule",
        urgency=0.0,
        reason=f"following the {entry.activity} schedule",
    )


def _home_id(resident: ResidentState) -> str:
    home_id = f"{resident.name.lower()}_home"
    if any(entry.location_id == home_id for entry in resident.schedule):
        return home_id
    return resident.location_id
