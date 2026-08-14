# Mind-Virus publication package

This directory contains the frozen evidence needed to reproduce the principal
Mind-Virus statistical results without an OpenAI API key or paid API calls.

## Included datasets

- `data/phase5_confirmatory_experiment.jsonl`: 120 matched condition-trials
  from the original confirmatory experiment.
- `data/phase6_confirmatory_analysis.json`: the committed statistical output
  derived from the Phase 5 dataset.
- `data/phase12_confirmatory_robustness.json`: 648 live decisions across 12
  claim/model/prompt cells from the robustness experiment.

These are frozen research artifacts. Runtime output continues to belong in the
ignored `results` directory.

## Reproduce the analysis

From the repository root, run:

```powershell
python -m scripts.reproduce_publication
```

The command verifies every dataset checksum, recomputes the Phase 6 and Phase
12 analyses, compares them with the committed outputs and report, and prints a
summary. It makes no network or API requests.

## Provenance and interpretation

The experiment design, caveats, and interpretation are documented in
`docs/research-report.md`, `docs/confirmatory-results.md`, and
`docs/phase12-confirmatory-robustness-results.md`. Dataset integrity hashes are
recorded in `SHA256SUMS`.

Research materials are available under CC BY 4.0; source code is available
under the MIT License. See `LICENSE-DATA.md` and the repository root `LICENSE`.
