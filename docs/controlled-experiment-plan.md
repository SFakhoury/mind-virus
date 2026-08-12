# Controlled Experiment Analysis Plan

This document freezes the principal outcomes and interpretation rules before
the final model-backed dataset is collected.

## Research Question

Does introducing a fixed proportion of skeptical agents reduce or slow the
propagation of unsupported claims through a society of memory-driven AI
agents?

## Experimental Conditions

### Baseline

All agents receive the same neutral base personality.

### Skeptical Society

The society uses the same neutral base personalities, but 35% of eligible
agents receive an additional evidence-seeking intervention.

Skeptic placement is selected reproducibly for each matched trial.

## Seed Claims

The experiment currently uses three unsupported claims:

1. A bakery giving away free bread
2. A library closing early because of a pipe leak
3. A bus route skipping a stop because of road work

The claims share hearsay framing but differ in topic and plausibility.

## Primary Outcome

The primary outcome is:

> Average number of agents exposed to the claim.

Exposure includes the original seed agent and every listener who later
hears the claim.

A negative skeptical-minus-baseline difference supports reduced
propagation.

## Secondary Outcomes

Secondary outcomes are:

- Maximum transmission generation
- Listener repetition rate
- Listener belief rate
- Average belief confidence
- Claim-specific effects
- Message mutation and uncertainty preservation

Secondary outcomes help explain the mechanism but do not replace the
primary outcome.

## Paired Design

Every baseline trial is paired with a skeptical trial using:

- The same claim
- The same trial number
- The same number of agents
- The same base personalities
- The same model
- The same experimental instructions
- A reproducibly assigned skeptic position

Paired skeptical-minus-baseline differences will be analyzed.

## Uncertainty

Mean paired differences will be reported with 95% bootstrap confidence
intervals.

A confidence interval containing zero means the collected data does not
clearly distinguish the conditions, even if their averages differ.

## Pilot Exclusion

Previous pilot runs are excluded from final confirmatory analysis because
they were used to discover and correct the methodology.

They remain documented as developmental evidence.

## Interpretation Rules

The final study will not claim that skepticism works merely because:

- One claim shows a difference
- One trial stops early
- The skeptical average is numerically lower
- A model explanation sounds persuasive

A conclusion requires repeated outcomes, uncertainty estimates, raw-data
inspection, and clear reporting of limitations.

## Planned Final Scale

The initial target is 20 paired trials per claim:

- 3 claims
- 20 trials per condition
- 2 conditions
- Up to 3 transmissions per trial
- Maximum of 360 model calls

Early stopping may reduce the actual call count.

The final scale may be adjusted before data collection if pilot variance,
cost, or methodological review indicates that a different design is
necessary. Once confirmatory collection begins, the outcome definitions
will not be changed in response to the results.
