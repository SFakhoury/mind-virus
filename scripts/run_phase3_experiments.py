from mind_virus.experiment import (
    run_comparison,
    summarize,
    write_results,
)


def main() -> None:
    results = run_comparison(
        trials=100,
        seed=2026,
        agent_count=12,
        skeptic_fraction=0.35,
    )
    summary = summarize(results)

    output = write_results(
        results,
        "results/phase3_results.csv",
    )

    baseline = summary["baseline"]
    skeptical = summary["skeptical"]

    print("PHASE 3: CONTROLLED PROPAGATION EXPERIMENT")
    print("-" * 48)
    print("Trials per condition: 100")
    print(
        "Baseline average believers: "
        f"{baseline['average_believers']:.2f}"
    )
    print(
        "Skeptical average believers: "
        f"{skeptical['average_believers']:.2f}"
    )
    print(
        "Baseline average generation: "
        f"{baseline['average_max_generation']:.2f}"
    )
    print(
        "Skeptical average generation: "
        f"{skeptical['average_max_generation']:.2f}"
    )
    print(f"Results written to: {output}")
    print("-" * 48)
    print("Phase 3 experiment completed successfully.")


if __name__ == "__main__":
    main()

