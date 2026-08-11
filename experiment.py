from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
import random
from statistics import mean

from agent import Agent
from claim import Claim


@dataclass(frozen=True)
class TrialResult:
    """Measurements from one propagation trial."""

    condition: str
    trial: int
    exposed_agents: int
    believing_agents: int
    max_generation: int
    total_agents: int

    @property
    def belief_rate(self) -> float:
        return self.believing_agents / self.total_agents


def run_trial(
    condition: str,
    trial: int,
    seed: int,
    agent_count: int = 12,
    skeptic_fraction: float = 0.0,
) -> TrialResult:
    """Run one reproducible claim-propagation trial."""
    if condition not in {"baseline", "skeptical"}:
        raise ValueError(
            "Condition must be baseline or skeptical."
        )

    if agent_count < 2:
        raise ValueError("Agent count must be at least 2.")

    if not 0.0 <= skeptic_fraction <= 1.0:
        raise ValueError(
            "Skeptic fraction must be between 0 and 1."
        )

    rng = random.Random(seed)

    agents = [
        Agent(
            name=f"Agent-{index}",
            personality=(
                "Cautious and evidence-seeking"
                if condition == "skeptical"
                else "Generally receptive"
            ),
        )
        for index in range(agent_count)
    ]

    skeptic_positions: set[int] = set()

    if condition == "skeptical":
        eligible_positions = list(range(1, agent_count))
        skeptic_count = round(
            len(eligible_positions) * skeptic_fraction
        )
        skeptic_positions = set(
            rng.sample(
                eligible_positions,
                k=skeptic_count,
            )
        )

    original = Claim(
        content=(
            "The bakery is reportedly giving away free bread."
        ),
        source_agent=agents[0].name,
        confidence=0.95,
    )

    agents[0].consider_claim(
        original,
        acceptance_threshold=0.5,
    )

    current_claim = original
    exposed_agents = 1
    believing_agents = 1

    for position in range(1, agent_count):
        speaker = agents[position - 1]
        listener = agents[position]

        listener.hear(
            speaker=speaker,
            message=current_claim.content,
            importance=6,
        )
        exposed_agents += 1

        acceptance_threshold = (
            0.8
            if position in skeptic_positions
            else 0.5
        )

        belief = listener.consider_claim(
            current_claim,
            acceptance_threshold=acceptance_threshold,
        )

        if belief is None:
            break

        believing_agents += 1

        next_confidence = max(
            0.0,
            current_claim.confidence
            - rng.uniform(0.02, 0.10),
        )

        current_claim = listener.repeat_claim(
            topic_id=current_claim.topic_id,
            content=current_claim.content,
            confidence=next_confidence,
        )

    return TrialResult(
        condition=condition,
        trial=trial,
        exposed_agents=exposed_agents,
        believing_agents=believing_agents,
        max_generation=current_claim.generation,
        total_agents=agent_count,
    )


def run_comparison(
    trials: int = 50,
    seed: int = 2026,
    agent_count: int = 12,
    skeptic_fraction: float = 0.35,
) -> list[TrialResult]:
    """Run matched baseline and skeptical trials."""
    if trials < 1:
        raise ValueError("Trials must be at least 1.")

    results: list[TrialResult] = []

    for trial in range(trials):
        trial_seed = seed + trial

        results.append(
            run_trial(
                condition="baseline",
                trial=trial,
                seed=trial_seed,
                agent_count=agent_count,
                skeptic_fraction=0.0,
            )
        )
        results.append(
            run_trial(
                condition="skeptical",
                trial=trial,
                seed=trial_seed,
                agent_count=agent_count,
                skeptic_fraction=skeptic_fraction,
            )
        )

    return results


def summarize(
    results: list[TrialResult],
) -> dict[str, dict[str, float]]:
    """Calculate average outcomes for each condition."""
    summary: dict[str, dict[str, float]] = {}

    for condition in ("baseline", "skeptical"):
        selected = [
            result
            for result in results
            if result.condition == condition
        ]

        if not selected:
            continue

        summary[condition] = {
            "average_exposed": mean(
                result.exposed_agents
                for result in selected
            ),
            "average_believers": mean(
                result.believing_agents
                for result in selected
            ),
            "average_belief_rate": mean(
                result.belief_rate
                for result in selected
            ),
            "average_max_generation": mean(
                result.max_generation
                for result in selected
            ),
        }

    return summary


def write_results(
    results: list[TrialResult],
    output_path: str | Path,
) -> Path:
    """Write reproducible trial measurements to CSV."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as output_file:
        writer = csv.DictWriter(
            output_file,
            fieldnames=[
                "condition",
                "trial",
                "exposed_agents",
                "believing_agents",
                "belief_rate",
                "max_generation",
                "total_agents",
            ],
        )
        writer.writeheader()

        for result in results:
            writer.writerow(
                {
                    "condition": result.condition,
                    "trial": result.trial,
                    "exposed_agents": result.exposed_agents,
                    "believing_agents": result.believing_agents,
                    "belief_rate": result.belief_rate,
                    "max_generation": result.max_generation,
                    "total_agents": result.total_agents,
                }
            )

    return path
