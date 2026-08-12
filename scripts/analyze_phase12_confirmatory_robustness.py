import json
from pathlib import Path

from mind_virus.confirmatory_robustness_analysis import analyze_confirmatory_robustness, render_confirmatory_robustness_report


def main() -> None:
    records = json.loads(Path("results/phase12_confirmatory_robustness.json").read_text(encoding="utf-8"))["records"]
    result = analyze_confirmatory_robustness(records)
    report = Path("docs/phase12-confirmatory-robustness-results.md")
    report.write_text(render_confirmatory_robustness_report(result), encoding="utf-8")
    print("PHASE 12: CONFIRMATORY ROBUSTNESS ANALYSIS")
    print("-" * 50)
    for label, effect in (("Primary repetition", result.primary), ("Secondary belief", result.secondary)):
        print(f"{label}: baseline={effect.baseline_rate:.3f}, skeptical={effect.skeptical_rate:.3f}")
        print(f"  difference={effect.difference:+.3f}, 95% CI=[{effect.confidence_interval_low:+.3f}, {effect.confidence_interval_high:+.3f}], p={effect.exact_p_value:.4g}")
    print(f"Records/cells: {result.records}/{result.cells}")
    print(f"Observed estimated cost: ${result.estimated_cost_usd:.4f}")
    print(f"Report written to: {report}")
    print("No API requests were made.")


if __name__ == "__main__":
    main()
