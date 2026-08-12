from mind_virus.analysis import load_and_analyze


def main() -> None:
    metrics = load_and_analyze(
        "results/ai_propagation_chain.json"
    )

    print("AI PROPAGATION ANALYSIS")
    print("-" * 42)
    print(f"Generations: {metrics.generations}")
    print(
        "Final similarity to original: "
        f"{metrics.original_similarity:.3f}"
    )
    print(
        "Average similarity per step: "
        f"{metrics.average_step_similarity:.3f}"
    )
    print(
        "Uncertainty mentions: "
        f"{metrics.uncertainty_mentions}"
    )
    print("-" * 42)
    print("Propagation analysis completed successfully.")


if __name__ == "__main__":
    main()
