from mind_virus.robustness_analysis import RobustnessObservation, summarize_robustness


def main() -> None:
    observations = [
        RobustnessObservation("model-a-neutral", "belief_rate", -0.12, -0.20, -0.04),
        RobustnessObservation("model-a-strict", "belief_rate", -0.08, -0.16, 0.00),
        RobustnessObservation("model-b-neutral", "belief_rate", -0.10, -0.19, -0.01),
        RobustnessObservation("model-b-strict", "belief_rate", -0.06, -0.15, 0.03),
    ]
    summary = summarize_robustness(
        observations, expected_direction="lower", minimum_consistency=0.8
    )
    output = summary.save("results/phase12_mock_robustness_summary.json")
    print("PHASE 12: ROBUSTNESS ANALYSIS VALIDATION")
    print("-" * 48)
    print(f"Cells analyzed: {summary.cells}")
    print(f"Direction consistency: {summary.direction_consistency:.3f}")
    print(f"Significant supporting cells: {summary.significant_supporting_cells}")
    print(f"Significant contradicting cells: {summary.significant_contradicting_cells}")
    print(f"Inconclusive cells: {summary.inconclusive_cells}")
    print(f"Mock conclusion survives: {summary.conclusion_survives}")
    print(f"Validation artifact: {output}")
    print("No API requests were made.")
    print("Analysis machinery passed. Real robustness data is still required.")


if __name__ == "__main__":
    main()
