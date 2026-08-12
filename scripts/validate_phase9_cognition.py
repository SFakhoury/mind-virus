from mind_virus.cognition_validation import (
    save_cognition_validation,
    validate_autonomous_cognition,
)


def main() -> None:
    town, report = validate_autonomous_cognition(days=3)
    output = save_cognition_validation(
        town,
        report,
        "results/phase9_autonomous_cognition.json",
    )
    print("PHASE 9: AUTONOMOUS COGNITION VALIDATION")
    print("-" * 46)
    print(f"Simulated days: {report.simulated_days}")
    print(f"Daily plans: {report.daily_plans} ({', '.join(report.plan_sources)})")
    print(f"Decision sources: {', '.join(report.decision_sources)}")
    print(f"Autonomous conversations: {report.conversations}")
    print(f"Reflections: {report.reflections}")
    print(f"Private memories: {report.memories}")
    print(f"Beliefs: {report.beliefs}")
    print(f"Routes valid: {report.routes_valid}")
    print(f"Conversation lineage valid: {report.conversation_lineage_valid}")
    print(f"Reflection lineage valid: {report.reflection_lineage_valid}")
    print(f"Decisions separated: {report.decisions_separated}")
    print(f"Validation passed: {report.passed}")
    print(f"Saved to: {output}")
    print("No API requests were made.")
    if not report.passed:
        raise RuntimeError("Phase 9 cognition validation failed.")


if __name__ == "__main__":
    main()
