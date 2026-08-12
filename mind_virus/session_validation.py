from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path

from mind_virus.persistent_session import PersistentSession


@dataclass(frozen=True)
class PersistentSessionValidation:
    passed: bool
    session_id_preserved: bool
    clock_continued: bool
    conversations_preserved: bool
    no_duplicate_conversations: bool
    memories_preserved: bool
    budget_preserved: bool
    rejection_log_preserved: bool
    checkpoint_is_valid_json: bool
    conversations_before_resume: int
    conversations_after_resume: int
    minute_before_resume: int
    minute_after_resume: int


def validate_persistent_session(
    checkpoint_path: str | Path,
    *,
    initial_minutes: int = 20,
    resumed_minutes: int = 5,
) -> PersistentSessionValidation:
    """Exercise checkpoint, reload, and continuation without API requests."""
    if initial_minutes < 1 or resumed_minutes < 1:
        raise ValueError("Validation durations must be positive.")
    path = Path(checkpoint_path)
    original = PersistentSession.create(path)
    original.tick(initial_minutes)
    reservation = original.budget.reserve(
        "validation-agent",
        estimated_input_tokens=8,
        estimated_output_tokens=4,
    )
    original.budget.reconcile(
        reservation.id,
        actual_input_tokens=6,
        actual_output_tokens=2,
    )
    original.town.dialogue_rejections.append(
        {
            "speaker": "validation-agent",
            "listener": "validation-listener",
            "reasons": ["synthetic persistence check"],
        }
    )
    original.pause()

    session_id = original.session_id
    minute_before = original.town.world.absolute_minute
    conversations_before = len(original.town.conversations)
    memories_before = {
        name: len(agent.memories)
        for name, agent in original.town.agents.items()
    }
    budget_before = original.budget.to_dict()
    rejection_log_before = list(original.town.dialogue_rejections)

    restored = PersistentSession.load(path)
    restored.town.process_new_interactions()
    no_duplicates = len(restored.town.conversations) == conversations_before
    restored.resume()
    restored.tick(resumed_minutes)

    memories_after = {
        name: len(agent.memories)
        for name, agent in restored.town.agents.items()
    }
    checks = {
        "session_id_preserved": restored.session_id == session_id,
        "clock_continued": (
            restored.town.world.absolute_minute == minute_before + resumed_minutes
        ),
        "conversations_preserved": (
            len(restored.town.conversations) >= conversations_before
        ),
        "no_duplicate_conversations": no_duplicates,
        "memories_preserved": all(
            memories_after[name] >= count for name, count in memories_before.items()
        ),
        "budget_preserved": restored.budget.to_dict() == budget_before,
        "rejection_log_preserved": (
            restored.town.dialogue_rejections == rejection_log_before
        ),
        "checkpoint_is_valid_json": _is_valid_checkpoint(path),
    }
    return PersistentSessionValidation(
        passed=all(checks.values()),
        **checks,
        conversations_before_resume=conversations_before,
        conversations_after_resume=len(restored.town.conversations),
        minute_before_resume=minute_before,
        minute_after_resume=restored.town.world.absolute_minute,
    )


def save_validation(
    validation: PersistentSessionValidation,
    output_path: str | Path,
) -> Path:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(asdict(validation), indent=2), encoding="utf-8")
    return output


def _is_valid_checkpoint(path: Path) -> bool:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return data.get("schema_version") == 1 and data.get("status") == "running"
