from mind_virus.world_validation import save_validation, validate_world


def main() -> None:
    world, report = validate_world(days=3)
    output = save_validation(
        world,
        report,
        "results/phase8_multiday_world.json",
    )
    print("PHASE 8: MULTI-DAY WORLD VALIDATION")
    print("-" * 44)
    print(f"Simulated days: {report.simulated_days}")
    print(f"World events triggered: {report.scheduled_events_triggered}")
    print(f"Departures / arrivals: {report.departures} / {report.arrivals}")
    print(f"Residents currently travelling: {report.active_travelers}")
    print(f"Needs valid: {report.needs_within_bounds}")
    print(f"Travel state valid: {report.travel_state_valid}")
    print(f"Replay identical: {report.replay_identical}")
    print(f"Validation passed: {report.passed}")
    print(f"Saved to: {output}")
    print("No API requests were made.")
    if not report.passed:
        raise RuntimeError("Multi-day world validation failed.")


if __name__ == "__main__":
    main()
