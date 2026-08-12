from pathlib import Path

from mind_virus.session_validation import save_validation, validate_persistent_session


def main() -> None:
    checkpoint = Path("results/phase10_validation_session.json")
    report_path = Path("results/phase10_persistent_session_validation.json")
    validation = validate_persistent_session(checkpoint)
    save_validation(validation, report_path)

    print("PHASE 10: PERSISTENT LIVE SESSION VALIDATION")
    print("-" * 48)
    print(f"Session ID preserved: {validation.session_id_preserved}")
    print(f"Clock continued: {validation.clock_continued}")
    print(f"Conversations preserved: {validation.conversations_preserved}")
    print(f"No duplicate conversations: {validation.no_duplicate_conversations}")
    print(f"Private memories preserved: {validation.memories_preserved}")
    print(f"Budget ledger preserved: {validation.budget_preserved}")
    print(f"Rejection log preserved: {validation.rejection_log_preserved}")
    print(f"Atomic checkpoint readable: {validation.checkpoint_is_valid_json}")
    print(f"Validation report: {report_path}")
    print("No API requests were made.")
    if not validation.passed:
        raise RuntimeError("Phase 10 persistent-session validation failed.")
    print("Phase 10 validation passed.")


if __name__ == "__main__":
    main()
