from __future__ import annotations

from dataclasses import asdict
from typing import Callable

from .calibrated_pilot import run_calibrated_pilot
from .config import ExperimentConfig
from .decision import (
    ModelUsage,
    TransmissionDecision,
)
from .journal import ResultJournal
from .seed_claims import SEED_CLAIMS


DecisionMaker = Callable[
    [object, object, str],
    TransmissionDecision,
]


FINAL_TRIALS_PER_CONDITION = 20
FINAL_EXPECTED_RECORDS = (
    len(SEED_CLAIMS)
    * 2
    * FINAL_TRIALS_PER_CONDITION
)
FINAL_MAXIMUM_API_CALLS = (
    FINAL_EXPECTED_RECORDS * 3
)
FINAL_MAXIMUM_COST_USD = 0.75


def planned_trial_keys() -> list[str]:
    """Return every confirmatory condition-trial identifier."""
    keys: list[str] = []

    for claim in SEED_CLAIMS:
        for trial in range(
            FINAL_TRIALS_PER_CONDITION
        ):
            for condition in (
                "baseline",
                "skeptical",
            ):
                keys.append(
                    ResultJournal.trial_key(
                        claim.id,
                        condition,
                        trial,
                    )
                )

    return keys


def journal_usage(
    journal: ResultJournal,
) -> ModelUsage:
    """Recover cumulative usage saved across earlier sessions."""
    usage = ModelUsage()

    for record in journal.records():
        saved_usage = record.get("usage", {})

        usage.calls += int(
            saved_usage.get("calls", 0)
        )
        usage.input_tokens += int(
            saved_usage.get("input_tokens", 0)
        )
        usage.output_tokens += int(
            saved_usage.get("output_tokens", 0)
        )

    return usage


def next_pending_key(
    journal: ResultJournal,
) -> str | None:
    """Return the next unfinished trial key."""
    completed = journal.completed_keys()

    for key in planned_trial_keys():
        if key not in completed:
            return key

    return None


def run_next_trial(
    journal: ResultJournal,
    decision_maker: DecisionMaker,
    *,
    cumulative_usage: ModelUsage,
) -> dict[str, object] | None:
    """Run and save one pending condition-trial."""
    key = next_pending_key(journal)

    if key is None:
        return None

    claim_id, condition, trial_text = key.split(":")
    trial = int(trial_text)

    claim = next(
        claim
        for claim in SEED_CLAIMS
        if claim.id == claim_id
    )

    if cumulative_usage.calls + 3 > (
        FINAL_MAXIMUM_API_CALLS
    ):
        raise RuntimeError(
            "The final experiment call ceiling "
            "would be exceeded."
        )

    if cumulative_usage.estimated_cost_usd >= (
        FINAL_MAXIMUM_COST_USD
    ):
        raise RuntimeError(
            "The final experiment cost ceiling "
            "has been reached."
        )

    before_calls = getattr(
        getattr(decision_maker, "usage", None),
        "calls",
        0,
    )
    before_input = getattr(
        getattr(decision_maker, "usage", None),
        "input_tokens",
        0,
    )
    before_output = getattr(
        getattr(decision_maker, "usage", None),
        "output_tokens",
        0,
    )

    config = ExperimentConfig(
        name="phase5-confirmatory",
        seed=2026 + trial,
        trials_per_condition=1,
        conditions=(condition,),
        agents_per_trial=4,
        skeptic_fraction=0.35,
        maximum_api_calls=3,
        maximum_cost_usd=0.02,
        estimated_output_tokens_per_call=180,
        dry_run=False,
    )

    result = run_calibrated_pilot(
        config=config,
        decision_maker=decision_maker,
        original_message=claim.message,
    )

    after_calls = getattr(
        getattr(decision_maker, "usage", None),
        "calls",
        before_calls + result.calls_made,
    )
    after_input = getattr(
        getattr(decision_maker, "usage", None),
        "input_tokens",
        before_input,
    )
    after_output = getattr(
        getattr(decision_maker, "usage", None),
        "output_tokens",
        before_output,
    )

    trial_usage = ModelUsage(
        calls=after_calls - before_calls,
        input_tokens=after_input - before_input,
        output_tokens=after_output - before_output,
    )

    maximum_generation = (
        result.maximum_generation_by_trial[
            f"{condition}:0"
        ]
    )

    records = [
        asdict(record)
        for record in result.records
    ]

    exposed_agents = 1 + len(records)
    belief_rate = (
        sum(
            record["believes_claim"]
            for record in records
        )
        / len(records)
    )
    repetition_rate = (
        sum(
            record["repeats_claim"]
            for record in records
        )
        / len(records)
    )

    saved_record: dict[str, object] = {
        "trial_key": key,
        "claim_id": claim.id,
        "claim_topic": claim.topic,
        "original_message": claim.message,
        "condition": condition,
        "trial": trial,
        "maximum_generation": maximum_generation,
        "exposed_agents": exposed_agents,
        "belief_rate": belief_rate,
        "repetition_rate": repetition_rate,
        "usage": asdict(trial_usage),
        "observed_cost_usd": (
            trial_usage.estimated_cost_usd
        ),
        "records": records,
    }

    journal.append(saved_record)

    cumulative_usage.calls += trial_usage.calls
    cumulative_usage.input_tokens += (
        trial_usage.input_tokens
    )
    cumulative_usage.output_tokens += (
        trial_usage.output_tokens
    )

    return saved_record
