from __future__ import annotations

from collections.abc import Callable

from .assignment import assign_agents
from .config import ExperimentConfig
from .controlled_pilot import (
    ControlledRecord,
    ControlledResult,
)
from .decision import TransmissionDecision


DecisionMaker = Callable[
    [object, object, str],
    TransmissionDecision,
]


def run_calibrated_pilot(
    config: ExperimentConfig,
    decision_maker: DecisionMaker,
) -> ControlledResult:
    """Run matched trials with a reproducible skeptic subset."""
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
        trial_seed = config.seed + trial

        for condition in config.conditions:
            agents, _ = assign_agents(
                condition=condition,
                count=config.agents_per_trial,
                skeptic_fraction=config.skeptic_fraction,
                seed=trial_seed,
            )

            message = original
            maximum_generation = 0

            for generation in range(
                1,
                config.agents_per_trial,
            ):
                if calls_made >= config.maximum_api_calls:
                    raise RuntimeError(
                        "Calibrated pilot reached its call limit."
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
