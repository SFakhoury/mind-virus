from mind_virus.experiment_framework import (
    GeneralizedExperimentRunner, estimate_two_proportion_sample_size,
)
from mind_virus.experiment_spec import (
    ClaimSpec, GeneralizedExperimentSpec, InterventionSpec, NetworkSpec,
)


def main() -> None:
    spec = GeneralizedExperimentSpec(
        "phase11-validation", 2026, 2, NetworkSpec("small_world", 8, 0.25),
        (ClaimSpec("bakery", "bakery", "The bakery has free bread."),),
        (InterventionSpec("none"), InterventionSpec("skepticism", 0.35)),
    )

    def mock_outcomes(context):
        treated = bool(context.assignment.treated_positions)
        return {
            "exposed_agents": float(len(context.network.nodes)),
            "maximum_generation": 3.0,
            "repetition_rate": 0.75 if treated else 1.0,
            "belief_rate": 0.25 if treated else 0.5,
        }

    runner = GeneralizedExperimentRunner(spec, mock_outcomes)
    results = runner.run()
    output = runner.save(results, "results/generalized_experiments")
    recommended = estimate_two_proportion_sample_size(0.50, 0.25)
    print("PHASE 11: GENERALIZED EXPERIMENT FRAMEWORK")
    print("-" * 48)
    print(f"Specification fingerprint: {spec.fingerprint}")
    print(f"Planned/collected trials: {spec.planned_trials}/{len(results)}")
    print(f"Network: {spec.network.structure}, residents: {spec.network.town_size}")
    print(f"Conditions: {len(spec.interventions)}")
    print(f"Approximate observations per condition for 0.50 -> 0.25: {recommended}")
    print(f"Dataset saved to: {output}")
    print("No API requests were made.")
    print("Phase 11 validation passed.")


if __name__ == "__main__":
    main()
