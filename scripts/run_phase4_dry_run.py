from mind_virus.config import ExperimentConfig


def main() -> None:
    config = ExperimentConfig()
    config.validate_budget()

    output = config.save(
        "results/phase4_dry_run_config.json"
    )

    print("PHASE 4: MODEL-BACKED PILOT CONFIGURATION")
    print("-" * 52)
    print(f"Model: {config.model}")
    print(
        "Conditions: "
        f"{', '.join(config.conditions)}"
    )
    print(
        "Trials per condition: "
        f"{config.trials_per_condition}"
    )
    print(
        "Agents per trial: "
        f"{config.agents_per_trial}"
    )
    print(
        "Planned API calls: "
        f"{config.planned_api_calls}"
    )
    print(
        "Maximum permitted calls: "
        f"{config.maximum_api_calls}"
    )
    print(
        "Estimated cost: "
        f"${config.estimated_cost_usd:.4f}"
    )
    print(
        "Maximum permitted cost: "
        f"${config.maximum_cost_usd:.2f}"
    )
    print(f"Dry run: {config.dry_run}")
    print(f"Configuration saved to: {output}")
    print("-" * 52)
    print("No API requests were made.")
    print("Phase 4 dry-run validation completed successfully.")


if __name__ == "__main__":
    main()
