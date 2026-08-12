# Phase 12 Multi-Claim Robustness Pilot

This diagnostic dataset contains 96 live structured decisions
across three claims, two models, two prompts, and matched baseline/skeptical
conditions. Each cell has four trials; it is not final confirmatory evidence.

| Claim | Model | Prompt | Belief difference | Repetition difference |
|---|---|---|---:|---:|
| bakery_free_bread | gpt-5.6-luna | evidence_explicit | +0.000 | -1.000 |
| bakery_free_bread | gpt-5.6-luna | neutral | -0.500 | -1.000 |
| bakery_free_bread | gpt-5.6-terra | evidence_explicit | +0.000 | -1.000 |
| bakery_free_bread | gpt-5.6-terra | neutral | +0.000 | -0.750 |
| bus_route_change | gpt-5.6-luna | evidence_explicit | +0.000 | -0.250 |
| bus_route_change | gpt-5.6-luna | neutral | -0.500 | -0.750 |
| bus_route_change | gpt-5.6-terra | evidence_explicit | +0.000 | -1.000 |
| bus_route_change | gpt-5.6-terra | neutral | +0.000 | -0.250 |
| library_early_closure | gpt-5.6-luna | evidence_explicit | +0.000 | -0.750 |
| library_early_closure | gpt-5.6-luna | neutral | -1.000 | -1.000 |
| library_early_closure | gpt-5.6-terra | evidence_explicit | +0.000 | -1.000 |
| library_early_closure | gpt-5.6-terra | neutral | +0.000 | -0.250 |

## Summary

- Cells with lower belief: 3/12
- Belief floor cells: 9/12
- Cells with lower repetition: 12/12
- Repetition floor cells: 0/12
- Cells contradicting the expected belief direction: 0
- Cells contradicting the expected repetition direction: 0
- Estimated API cost: $0.0804

Skeptical listeners repeated no tested claim. Reductions were observable only
where baseline agents had a nonzero rate; zero-baseline cells are floor effects,
not evidence that skepticism failed or reversed direction. Model and prompt
choice materially changed baseline behavior. This small direct-decision pilot
does not replace a powered, full-chain confirmatory robustness experiment.
