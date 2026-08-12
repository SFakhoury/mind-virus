from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json
from pathlib import Path


@dataclass(frozen=True)
class Location:
    id: str
    name: str
    x: float
    y: float

    def __post_init__(self) -> None:
        if not self.id.strip() or not self.name.strip():
            raise ValueError("Location id and name cannot be empty.")
        if not 0.0 <= self.x <= 1.0 or not 0.0 <= self.y <= 1.0:
            raise ValueError("Location coordinates must be between 0 and 1.")


@dataclass(frozen=True)
class Route:
    start: str
    end: str
    travel_minutes: int

    def __post_init__(self) -> None:
        if self.start == self.end:
            raise ValueError("A route must connect different locations.")
        if self.travel_minutes < 1:
            raise ValueError("Travel time must be at least one minute.")


@dataclass(frozen=True)
class ScheduleEntry:
    minute_of_day: int
    location_id: str
    activity: str

    def __post_init__(self) -> None:
        if not 0 <= self.minute_of_day < 1440:
            raise ValueError("Schedule minute must be within one day.")
        if not self.location_id.strip() or not self.activity.strip():
            raise ValueError("Schedule location and activity cannot be empty.")


@dataclass
class ResidentState:
    name: str
    location_id: str
    schedule: tuple[ScheduleEntry, ...]
    destination_id: str | None = None
    activity: str = "idle"
    travel_remaining: int = 0

    def next_schedule_entry(self, minute_of_day: int) -> ScheduleEntry:
        eligible = [
            entry for entry in self.schedule
            if entry.minute_of_day <= minute_of_day
        ]
        if eligible:
            return max(eligible, key=lambda entry: entry.minute_of_day)
        return max(self.schedule, key=lambda entry: entry.minute_of_day)


@dataclass
class WorldState:
    locations: dict[str, Location]
    routes: tuple[Route, ...]
    residents: dict[str, ResidentState]
    absolute_minute: int = 480
    event_log: list[dict[str, object]] = field(default_factory=list)

    @property
    def day(self) -> int:
        return self.absolute_minute // 1440 + 1

    @property
    def minute_of_day(self) -> int:
        return self.absolute_minute % 1440

    def travel_minutes(self, start: str, end: str) -> int:
        if start == end:
            return 0
        for route in self.routes:
            if {route.start, route.end} == {start, end}:
                return route.travel_minutes
        raise ValueError(f"No direct route from {start} to {end}.")

    def tick(self, minutes: int = 1) -> None:
        if minutes < 1:
            raise ValueError("Tick duration must be at least one minute.")
        for _ in range(minutes):
            self.absolute_minute += 1
            for resident in self.residents.values():
                self._advance_resident(resident)

    def _advance_resident(self, resident: ResidentState) -> None:
        if resident.travel_remaining > 0:
            resident.travel_remaining -= 1
            if resident.travel_remaining == 0:
                resident.location_id = resident.destination_id or resident.location_id
                resident.destination_id = None
                self._record("arrival", resident)
            return

        entry = resident.next_schedule_entry(self.minute_of_day)
        resident.activity = entry.activity
        if entry.location_id == resident.location_id:
            return
        resident.destination_id = entry.location_id
        resident.travel_remaining = self.travel_minutes(
            resident.location_id,
            entry.location_id,
        )
        self._record("departure", resident)

    def _record(self, event_type: str, resident: ResidentState) -> None:
        self.event_log.append(
            {
                "minute": self.absolute_minute,
                "day": self.day,
                "type": event_type,
                "resident": resident.name,
                "location": resident.location_id,
                "destination": resident.destination_id,
                "activity": resident.activity,
            }
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "absolute_minute": self.absolute_minute,
            "day": self.day,
            "minute_of_day": self.minute_of_day,
            "locations": {
                key: asdict(value) for key, value in self.locations.items()
            },
            "routes": [asdict(route) for route in self.routes],
            "residents": {
                key: asdict(value) for key, value in self.residents.items()
            },
            "event_log": list(self.event_log),
        }

    def save(self, path: str | Path) -> Path:
        output = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")
        return output


def build_default_world() -> WorldState:
    locations = {
        "alice_home": Location("alice_home", "Alice's Home", 0.18, 0.72),
        "bob_home": Location("bob_home", "Bob's Home", 0.35, 0.72),
        "charlie_home": Location("charlie_home", "Charlie's Home", 0.72, 0.72),
        "dana_home": Location("dana_home", "Dana's Home", 0.86, 0.72),
        "bakery": Location("bakery", "Sunrise Bakery", 0.18, 0.18),
        "library": Location("library", "Maple Library", 0.76, 0.18),
        "town_hall": Location("town_hall", "Town Hall", 0.18, 0.82),
        "bus_stop": Location("bus_stop", "Bus Stop", 0.76, 0.82),
    }
    routes = tuple(
        Route(start, end, minutes)
        for start, end, minutes in (
            ("alice_home", "town_hall", 8),
            ("bob_home", "bakery", 10),
            ("charlie_home", "library", 9),
            ("dana_home", "town_hall", 12),
            ("town_hall", "bakery", 7),
            ("town_hall", "library", 11),
            ("town_hall", "bus_stop", 9),
        )
    )
    residents = {
        "Alice": ResidentState(
            "Alice", "alice_home",
            (
                ScheduleEntry(0, "alice_home", "sleeping"),
                ScheduleEntry(480, "town_hall", "reporting"),
                ScheduleEntry(1020, "alice_home", "personal time"),
            ),
        ),
        "Bob": ResidentState(
            "Bob", "bob_home",
            (
                ScheduleEntry(0, "bob_home", "sleeping"),
                ScheduleEntry(420, "bakery", "working"),
                ScheduleEntry(960, "bob_home", "personal time"),
            ),
        ),
        "Charlie": ResidentState(
            "Charlie", "charlie_home",
            (
                ScheduleEntry(0, "charlie_home", "sleeping"),
                ScheduleEntry(540, "library", "working"),
                ScheduleEntry(1020, "charlie_home", "personal time"),
            ),
        ),
        "Dana": ResidentState(
            "Dana", "dana_home",
            (
                ScheduleEntry(0, "dana_home", "sleeping"),
                ScheduleEntry(510, "town_hall", "planning"),
                ScheduleEntry(1050, "dana_home", "personal time"),
            ),
        ),
    }
    return WorldState(locations, routes, residents)
