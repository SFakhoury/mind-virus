from __future__ import annotations

from collections.abc import Callable
from dataclasses import asdict, dataclass
import json
from pathlib import Path

from .agent import Agent
from .config import ExperimentConfig
from .decision import TransmissionDecision
from .pilot import build_agents


DecisionMaker = Callable[
    [Agent, Agent, str],
    TransmissionDecision,
]


@dataclass(frozen=True)
class ControlledRecord:
    condition: str
    trial: int
    generation: int
    speaker: str
    listener: str
    input_message: str
    remembered_message: str
    believes_claim: bool
    repeats_claim: bool
    belief_confidence: float
    reason: str


@dataclass(frozen=True)
class ControlledResult:
    records: tuple[ControlledRecord, ...]
    calls_made: int
    maximum_generation_by_trial: dict[str, int]


def run_controlled_pilot(
    config: ExperimentConfig,
    decision_maker: DecisionMaker,
) -> ControlledResult:
    """Run propagation that stops when a listener will not repeat."""
    if not callable(decision_maker):
        raise TypeError("Decision maker must be callable.")

    config.validate_budget()

    records: list[ControlledRecord] = []
    maximum_generations: dict[str, int] = {}
    calls_made = 0

    original = (
        "I heard the bakery is giving away free bread."
    )

    for trial in range(config.trials_per_condition):
        for condition in config.conditions:
            agents = build_agents(
                condition,
                config.agents_per_trial,
            )
            message = original
            maximum_generation = 0

            for generation in range(
                1,
                config.agents_per_trial,
            ):
                if calls_made >= config.maximum_api_calls:
                    raise RuntimeError(
                        "Controlled pilot reached its call limit."
                    )

                speaker = agents[generation - 1]
                listener = agents[generation]

                decision = decision_maker(
                    listener,
                    speaker,
                    message,
                )
                calls_made += 1

                listener.hear(
                    speaker=speaker,
                    message=message,
                    importance=6,
                    interpretation=decision.remembered_message,
                )

                records.append(
                    ControlledRecord(
                        condition=condition,
                        trial=trial,
                        generation=generation,
                        speaker=speaker.name,
                        listener=listener.name,
                        input_message=message,
                        remembered_message=(
                            decision.remembered_message
                        ),
                        believes_claim=decision.believes_claim,
                        repeats_claim=decision.repeats_claim,
                        belief_confidence=(
                            decision.belief_confidence
                        ),
                        reason=decision.reason,
                    )
                )

                maximum_generation = generation

                if not decision.repeats_claim:
                    break

                message = decision.remembered_message

            maximum_generations[
                f"{condition}:{trial}"
            ] = maximum_generation

    return ControlledResult(
        records=tuple(records),
        calls_made=calls_made,
        maximum_generation_by_trial=maximum_generations,
    )


def save_controlled_result(
    result: ControlledResult,
    path: str | Path,
) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)

    output.write_text(
        json.dumps(
            {
                "calls_made": result.calls_made,
                "maximum_generation_by_trial": (
                    result.maximum_generation_by_trial
                ),
                "records": [
                    asdict(record)
                    for record in result.records
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    return output
