# Phase 12 Confirmatory Robustness Results

This preregistered confirmatory dataset contains 648 live model decisions across 12 claim/model/prompt cells, with 27 matched trials per condition in every cell. Effects are skeptical minus baseline.

## Primary outcome: repetition

Baseline 0.830; skeptical 0.000; difference -0.830; 95% bootstrap CI [-0.870, -0.787]; exact paired p=2.108e-81.

## Secondary outcome: belief

Baseline 0.117; skeptical 0.000; difference -0.117; 95% bootstrap CI [-0.154, -0.083]; exact paired p=7.276e-12.

| Claim | Model | Prompt | Repetition difference | Belief difference |
|---|---|---|---:|---:|
| bakery_free_bread | gpt-5.6-luna | evidence_explicit | -0.963 | +0.000 |
| bakery_free_bread | gpt-5.6-luna | neutral | -0.926 | -0.222 |
| bakery_free_bread | gpt-5.6-terra | evidence_explicit | -1.000 | +0.000 |
| bakery_free_bread | gpt-5.6-terra | neutral | -0.815 | +0.000 |
| bus_route_change | gpt-5.6-luna | evidence_explicit | -0.741 | -0.037 |
| bus_route_change | gpt-5.6-luna | neutral | -0.815 | -0.407 |
| bus_route_change | gpt-5.6-terra | evidence_explicit | -1.000 | +0.000 |
| bus_route_change | gpt-5.6-terra | neutral | -0.519 | +0.000 |
| library_early_closure | gpt-5.6-luna | evidence_explicit | -0.926 | -0.037 |
| library_early_closure | gpt-5.6-luna | neutral | -1.000 | -0.704 |
| library_early_closure | gpt-5.6-terra | evidence_explicit | -1.000 | +0.000 |
| library_early_closure | gpt-5.6-terra | neutral | -0.259 | +0.000 |

## Interpretation

Negative differences indicate that skepticism reduced the outcome. Repetition and belief are reported separately because an agent may repeat an unverified claim without believing it. Exact McNemar tests use matched binary decisions; confidence intervals are paired bootstrap intervals. Estimated API cost: $0.5439.
