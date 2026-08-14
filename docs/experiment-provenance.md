# Experiment Provenance

This document traces the published Mind-Virus findings back to their frozen
designs, raw records, analysis code, and reports.

## Original confirmatory experiment

| Stage | Artifact |
| --- | --- |
| Design and treatment rationale | `docs/controlled-experiment-plan.md` |
| Methodological decisions and corrections | `docs/methodology-notes.md` |
| Frozen condition-trial records | `publication/data/phase5_confirmatory_experiment.jsonl` |
| Analysis implementation | `scripts/analyze_confirmatory_experiment.py` |
| Frozen analysis output | `publication/data/phase6_confirmatory_analysis.json` |
| Human-readable result | `docs/confirmatory-results.md` |
| Integrity manifest | `publication/SHA256SUMS` |

The dataset contains 120 condition-trials: three claims, 20 matched trials per
condition and claim, and two conditions. The principal published observation
was that pooled belief decreased under skeptical treatment while exposure and
maximum propagation depth did not.

## Confirmatory robustness experiment

| Stage | Artifact |
| --- | --- |
| Frozen protocol | `docs/phase12-confirmatory-robustness-protocol.json` |
| Collection implementation | `mind_virus/confirmatory_robustness.py` |
| Frozen decision records | `publication/data/phase12_confirmatory_robustness.json` |
| Analysis implementation | `mind_virus/confirmatory_robustness_analysis.py` |
| Human-readable result | `docs/phase12-confirmatory-robustness-results.md` |
| Integrity manifest | `publication/SHA256SUMS` |

The robustness dataset contains 648 decisions across three claims, two models,
two prompt variants, two conditions, and 27 matched trials per cell. It was
collected separately from pilot data and analyzed with paired binary effects,
bootstrap intervals, and exact McNemar tests.

## Reproduction

Run the following command from a fresh repository clone:

```powershell
python -m scripts.reproduce_publication
```

The command verifies the SHA-256 digest of every frozen dataset, recomputes
both analyses, and checks the recomputed outputs against the published
artifacts. It makes no network requests and requires no API key.

## Boundaries of the evidence

- These results describe model behavior in the specified simulations, not
  misinformation behavior in human communities.
- The experiments test prompt-based skeptical interventions, not every
  possible fact-checking or evidence-seeking intervention.
- Model, prompt, claim, and network choices define the population to which the
  findings directly apply.
- Pilot records were used for debugging and calibration and are not silently
  mixed into the confirmatory datasets.
