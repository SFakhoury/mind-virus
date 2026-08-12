from mind_virus.statistics import paired_bootstrap


def print_estimate(name, baseline, skeptical):
    estimate = paired_bootstrap(
        baseline,
        skeptical,
        iterations=10_000,
        seed=2026,
    )

    print(name)
    print(
        "  Baseline mean: "
        f"{estimate.baseline_mean:.3f}"
    )
    print(
        "  Skeptical mean: "
        f"{estimate.skeptical_mean:.3f}"
    )
    print(
        "  Paired difference: "
        f"{estimate.mean_difference:.3f}"
    )
    print(
        "  Diagnostic 95% interval: "
        f"[{estimate.confidence_interval_low:.3f}, "
        f"{estimate.confidence_interval_high:.3f}]"
    )


def main() -> None:
    print("PHASE 5: PILOT EFFECT INTERPRETATION")
    print("-" * 52)

    print_estimate(
        "Bakery exposure",
        baseline=[4.0, 4.0, 4.0],
        skeptical=[4.0, 4.0, 3.0],
    )
    print_estimate(
        "Library exposure",
        baseline=[4.0, 4.0, 4.0],
        skeptical=[4.0, 4.0, 4.0],
    )
    print_estimate(
        "Bus exposure",
        baseline=[4.0, 4.0, 4.0],
        skeptical=[4.0, 4.0, 4.0],
    )

    print("-" * 52)
    print(
        "These intervals describe tiny pilot samples "
        "and are not final evidence."
    )
    print("No API requests were made.")


if __name__ == "__main__":
    main()
