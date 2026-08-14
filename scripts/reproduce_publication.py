from __future__ import annotations

import hashlib
import json
from pathlib import Path

from mind_virus.confirmatory_robustness_analysis import (
    analyze_confirmatory_robustness,
    render_confirmatory_robustness_report,
)
from scripts.analyze_confirmatory_experiment import analyze_records, load_records


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "publication"
DATA = PACKAGE / "data"


def verify_checksums() -> None:
    entries = (PACKAGE / "SHA256SUMS").read_text(encoding="utf-8").splitlines()
    for entry in entries:
        expected, relative_path = entry.split("  ", 1)
        path = PACKAGE / relative_path
        # Git may materialize text files with CRLF on Windows and LF on Linux.
        # Hash a canonical UTF-8/LF representation so integrity verification
        # describes the dataset content rather than the checkout platform.
        canonical = path.read_text(encoding="utf-8").replace("\r\n", "\n")
        observed = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        if observed != expected:
            raise ValueError(f"Checksum mismatch: {relative_path}")


def reproduce_phase6() -> dict[str, object]:
    records = load_records(DATA / "phase5_confirmatory_experiment.jsonl")
    reproduced = analyze_records(records)
    expected = json.loads(
        (DATA / "phase6_confirmatory_analysis.json").read_text(encoding="utf-8")
    )
    if reproduced != expected:
        raise ValueError("Recomputed Phase 6 analysis differs from the archive.")
    return reproduced


def reproduce_phase12():
    payload = json.loads(
        (DATA / "phase12_confirmatory_robustness.json").read_text(encoding="utf-8")
    )
    reproduced = analyze_confirmatory_robustness(payload["records"])
    expected_report = (ROOT / "docs" / "phase12-confirmatory-robustness-results.md").read_text(
        encoding="utf-8"
    )
    if render_confirmatory_robustness_report(reproduced).strip() != expected_report.strip():
        raise ValueError("Recomputed Phase 12 report differs from the published report.")
    return reproduced


def main() -> None:
    verify_checksums()
    phase6 = reproduce_phase6()
    phase12 = reproduce_phase12()
    pooled = phase6["pooled"]

    print("MIND-VIRUS PUBLICATION REPRODUCTION")
    print("-" * 42)
    print("Dataset checksums: verified")
    print(f"Phase 6 condition-trials: {phase6['design']['condition_trials']}")
    print(
        "Phase 6 pooled belief difference: "
        f"{pooled['belief_rate']['mean_difference']:+.3f}"
    )
    print(f"Phase 12 records/cells: {phase12.records}/{phase12.cells}")
    print(f"Phase 12 repetition difference: {phase12.primary.difference:+.3f}")
    print(f"Phase 12 belief difference: {phase12.secondary.difference:+.3f}")
    print("Reproduction passed. No API requests were made.")


if __name__ == "__main__":
    main()
