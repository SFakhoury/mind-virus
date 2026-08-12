from __future__ import annotations

from dataclasses import dataclass
import random

from mind_virus.agent import Agent
from mind_virus.experiment_spec import InterventionSpec


BASE_PERSONALITY = (
    "Social, attentive, independent-minded, and willing to discuss "
    "interesting information."
)

INTERVENTION_INSTRUCTIONS = {
    "skepticism": (
        "Distinguishes unsupported claims from established facts and seeks "
        "corroborating evidence before believing or repeating them."
    ),
    "fact_check": (
        "Actively checks uncertain claims against direct or authoritative "
        "evidence and clearly communicates corrections."
    ),
    "inoculation": (
        "Has been warned that misleading claims may circulate and watches for "
        "unsupported evidence, emotional framing, and repeated hearsay."
    ),
}


@dataclass(frozen=True)
class InterventionAssignment:
    intervention_type: str
    intensity: float
    eligible_positions: tuple[int, ...]
    treated_positions: tuple[int, ...]
    assignment_seed: int

    def is_treated(self, position: int) -> bool:
        return position in self.treated_positions


def assign_intervention(
    town_size: int,
    intervention: InterventionSpec,
    assignment_seed: int,
    *,
    source_position: int = 0,
) -> InterventionAssignment:
    """Select treated residents reproducibly while holding the source fixed."""
    if town_size < 2:
        raise ValueError("Town size must be at least 2.")
    if source_position not in range(town_size):
        raise ValueError("Source position must be inside the town.")
    eligible = tuple(position for position in range(town_size) if position != source_position)
    treated_count = (
        0
        if intervention.type == "none"
        else round(len(eligible) * intervention.intensity)
    )
    if intervention.type != "none" and treated_count == 0:
        treated_count = 1
    treated = tuple(sorted(random.Random(assignment_seed).sample(eligible, treated_count)))
    return InterventionAssignment(
        intervention.type,
        intervention.intensity,
        eligible,
        treated,
        assignment_seed,
    )


def build_experimental_agents(
    town_size: int,
    intervention: InterventionSpec,
    assignment_seed: int,
    *,
    source_position: int = 0,
) -> tuple[list[Agent], InterventionAssignment]:
    assignment = assign_intervention(
        town_size, intervention, assignment_seed, source_position=source_position
    )
    agents: list[Agent] = []
    for position in range(town_size):
        personality = BASE_PERSONALITY
        if assignment.is_treated(position):
            personality = (
                f"{personality} {INTERVENTION_INSTRUCTIONS[intervention.type]}"
            )
        agents.append(Agent(f"Agent-{position}", personality))
    return agents, assignment
