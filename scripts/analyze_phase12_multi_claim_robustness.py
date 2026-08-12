import json
from pathlib import Path

from mind_virus.multi_claim_robustness_analysis import (
    analyze_multi_claim_robustness, render_multi_claim_report,
)


def main() -> None:
    source = Path("results/phase12_multi_claim_robustness.json")
    records = json.loads(source.read_text(encoding="utf-8"))["records"]
    analysis = analyze_multi_claim_robustness(records)
    report = Path("docs/phase12-multi-claim-robustness.md")
    report.write_text(render_multi_claim_report(analysis), encoding="utf-8")
    print("PHASE 12: MULTI-CLAIM ROBUSTNESS ANALYSIS")
    print("-" * 48)
    print(f"Records/cells: {analysis.records}/{len(analysis.cells)}")
    print(f"Belief reductions: {analysis.belief_reduction_cells}/{len(analysis.cells)}")
    print(f"Belief floors: {analysis.belief_floor_cells}/{len(analysis.cells)}")
    print(f"Repetition reductions: {analysis.repetition_reduction_cells}/{len(analysis.cells)}")
    print(f"Repetition floors: {analysis.repetition_floor_cells}/{len(analysis.cells)}")
    print(f"Contradictory repetition cells: {analysis.contradictory_repetition_cells}")
    print(f"Report written to: {report}")
    print("No API requests were made.")


if __name__ == "__main__":
    main()
