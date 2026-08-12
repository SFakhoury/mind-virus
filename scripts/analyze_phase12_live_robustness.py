import json
from pathlib import Path

from mind_virus.live_robustness_analysis import (
    analyze_live_robustness, render_live_pilot_report,
)


def main() -> None:
    source = Path("results/phase12_live_robustness_pilot.json")
    records = json.loads(source.read_text(encoding="utf-8"))["records"]
    analysis = analyze_live_robustness(records)
    report = Path("docs/phase12-live-robustness-pilot.md")
    report.write_text(render_live_pilot_report(analysis), encoding="utf-8")
    print("PHASE 12: LIVE ROBUSTNESS PILOT ANALYSIS")
    print("-" * 48)
    print(f"Records: {analysis.records}")
    print(f"Model/prompt cells: {len(analysis.cells)}")
    print(f"Belief direction consistency: {analysis.belief_direction_consistency:.3f}")
    print(f"Repetition direction consistency: {analysis.repetition_direction_consistency:.3f}")
    print(f"Observed estimated cost: ${analysis.estimated_cost_usd:.4f}")
    print(f"Report written to: {report}")
    print("No API requests were made.")


if __name__ == "__main__":
    main()
