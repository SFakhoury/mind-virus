from __future__ import annotations

from collections.abc import Callable
from dataclasses import asdict, dataclass
import json
from pathlib import Path

from .agent import Agent
from .config import ExperimentConfig


Interpreter = Callable[[Agent, Agent, str], str]


@dataclass(frozen=True)
class PilotRecord:
    """One transmission recorded during a pilot experiment."""

    condition: str
    trial: int
    generation: int
    speaker: str
    listener: str
    speaker_personality: str
    listener_personality: str
    input_message: str
    interpreted_message: str


@dataclass(frozen=True)
class PilotResult:
    """Complete output and usage information from a pilot run."""

    records: tuple[PilotRecord, ...]
    api_calls: int
    dry_run: bool


def build_agents(
    condition: str,
    count: int,
) -> list[Agent]:
    """Create matched agents, changing only skepticism."""
    if condition not in {"baseline", "skeptical"}:
        raise ValueError(
            "Condition must be baseline or skeptical."
        )

    agents: list[Agent] = []

    for index in range(count):
        if index == 0:
            personality = (
                "Social, confident, and willing to share information"
            )
        elif condition == "skeptical":
            personality = (
                "Skeptical, evidence-seeking, and careful "
                "not to treat hearsay as fact"
            )
        else:
            personality = (
                "Social, receptive, and moderately trusting "
                "of information from others"
            )

        agents.append(
            Agent(
                name=f"Agent-{index}",
                personality=personality,
            )
        )

    return agents


def run_pilot(
    config: ExperimentConfig,
    interpreter: Interpreter,
) -> PilotResult:
    """Run matched propagation chains under configured limits."""
    if not callable(interpreter):
        raise TypeError("Interpreter must be callable.")

    config.validate_budget()

    records: list[PilotRecord] = []
    call_count = 0

    original_message = (
        "I heard the bakery is giving away free bread."
    )

    for trial in range(config.trials_per_condition):
        for condition in config.conditions:
            agents = build_agents(
                condition=condition,
                count=config.agents_per_trial,
            )
            message = original_message

            for generation in range(
                1,
                config.agents_per_trial,
            ):
                if call_count >= config.maximum_api_calls:
                    raise RuntimeError(
                        "Pilot reached the maximum API-call limit."
                    )

                speaker = agents[generation - 1]
                listener = agents[generation]

                interpretation = interpreter(
                    listener,
                    speaker,
                    message,
                ).strip()

                call_count += 1

                if not interpretation:
                    raise ValueError(
                        "Interpreter returned an empty message."
                    )

                listener.hear(
                    speaker=speaker,
                    message=message,
                    importance=6,
                    interpretation=interpretation,
                )

                records.append(
                    PilotRecord(
                        condition=condition,
                        trial=trial,
                        generation=generation,
                        speaker=speaker.name,
                        listener=listener.name,
                        speaker_personality=speaker.personality,
                        listener_personality=listener.personality,
                        input_message=message,
                        interpreted_message=interpretation,
                    )
                )

                message = interpretation

    return PilotResult(
        records=tuple(records),
        api_calls=call_count,
        dry_run=config.dry_run,
    )


def save_pilot_result(
    result: PilotResult,
    path: str | Path,
) -> Path:
    """Save all transmissions and usage data to JSON."""
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)

    data = {
        "api_calls": result.api_calls,
        "dry_run": result.dry_run,
        "records": [
            asdict(record)
            for record in result.records
        ],
    }

    output.write_text(
        json.dumps(data, indent=2),
        encoding="utf-8",
    )

    return output
