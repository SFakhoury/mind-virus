# Phase 12 Live Robustness Pilot

This diagnostic pilot compared two models and two prompt variants across
matched baseline and skeptical listener conditions. It contains
32 structured model decisions and is not a final confirmatory dataset.

| Model | Prompt | Base belief | Skeptic belief | Difference | Base repeat | Skeptic repeat | Difference |
|---|---|---:|---:|---:|---:|---:|---:|
| gpt-5.6-luna | evidence_explicit | 0.000 | 0.000 | +0.000 | 1.000 | 0.000 | -1.000 |
| gpt-5.6-luna | neutral | 0.250 | 0.000 | -0.250 | 0.500 | 0.000 | -0.500 |
| gpt-5.6-terra | evidence_explicit | 0.000 | 0.000 | +0.000 | 1.000 | 0.000 | -1.000 |
| gpt-5.6-terra | neutral | 0.000 | 0.000 | +0.000 | 0.750 | 0.000 | -0.750 |

## Pilot interpretation

- Belief-effect direction consistency: 0.250
- Repetition-effect direction consistency: 1.000
- Input tokens: 6064
- Output tokens: 2871
- Estimated cost: $0.0261

Skepticism reduced repetition in every model/prompt cell. Belief was already
absent in most baseline cells, producing a floor effect; therefore this pilot
does not establish a robust belief reduction. The sample is small, uses one
claim, and evaluates one listener decision rather than full-chain propagation.
