# Mind-Virus v2.0: Full Research Platform Roadmap

Version 1.1 is the completed research prototype. Version 2.0 expands it into
a persistent, autonomous, deployable research platform. A polished screen or
a single successful model run is not sufficient to complete a phase.

## Phase 8: Persistent World Engine

- Explicit locations, coordinates, routes, and travel times
- Simulation clock with configurable tick duration
- Resident positions, needs, destinations, and daily schedules
- Social graph with relationship strength and interaction history
- World events independent of misinformation claims
- Complete JSON save, resume, and deterministic replay
- UI driven by server world state rather than browser-only movement

Completion requires unit tests, a multi-day deterministic simulation, a
save/resume equivalence test, and a replay producing identical state.

## Phase 9: Autonomous Cognition

**Status: complete.** Validated across a deterministic three-day run with
auditable daily plans, need-driven actions, agent-selected partners and
topics, contextual memory retrieval, grounded conversation lineage,
separate listener belief/repetition decisions, and evidence-linked
reflections.

- Daily planning from personality, role, needs, relationships, and memories
- Retrieval tied to the current place, person, goal, and conversation
- Reflection that produces higher-level memories from accumulated experience
- Agent-selected conversation partners and topics
- Distinct speech generation, listener interpretation, belief, and repetition
- Grounded actions constrained by known world state

Completion requires agents to produce different schedules and interactions
from different internal states without hard-coded conversation chains.

## Phase 10: Persistent Live AI Sessions

**Status: complete.** Persistent sessions now checkpoint and resume the world,
agent cognition, conversations, event cursor, API budgets, and rejected model
outputs without losing or duplicating processed encounters.

- Resumable multi-day model-backed town runs
- Per-agent and per-session budgets, rate limits, and failure recovery
- Structured action and dialogue schemas
- Grounding validation and rejected-output logging
- Complete lineage from prompt context to decision and resulting memory
- Human controls for pause, inspection, intervention, and replay

Completion requires an interrupted live run to resume without losing or
duplicating events, plus an auditable cost and decision record.

## Phase 11: Generalized Experimental Framework

**Status: complete.** A validated, fingerprinted experiment specification
now defines networks, town sizes, claims, evidence conditions, interventions,
intensities, outcomes, dataset stage, trial counts, and random seed. It now
builds deterministic chain, ring, complete, and connected small-world social
networks directly from that specification. Matched condition-trials are now
expanded and randomized reproducibly, with shared assignment and network seeds
preserved across each matched comparison. Control, skepticism, fact-checking,
and inoculation interventions can now be assigned at reproducible intensities
while holding the original claim source constant. Confirmatory hypotheses and
outcome definitions can now be frozen in tamper-evident preregistrations that
cannot be silently replaced or created from pilot configurations.
The generalized runner now assembles every configured condition, validates
frozen outcomes, separates pilot and confirmatory datasets, enforces matching
preregistrations, records provenance, and provides two-proportion power guidance.

- Multiple social-network structures and town sizes
- Multiple misinformation topics and evidence conditions
- Several intervention types and treatment intensities
- Preregistered hypotheses and frozen outcome definitions
- Pilot and confirmatory datasets kept strictly separate
- Automated matched trials, randomization, and power analysis

Completion requires experiments that are configuration-driven rather than
implemented as one-off scripts.

## Phase 12: Robustness and Research Validation

**Status: in progress.** Reproducible robustness manifests now cross model,
prompt, temperature, and repetition settings in randomized execution order,
with every cell tied to the frozen experiment specification.

- Multiple model families or versions
- Prompt and temperature sensitivity analysis
- Larger samples based on power and variance estimates
- Effect sizes, uncertainty intervals, multiple-comparison handling
- Mutation, calibration, belief, exposure, and network-level measurements
- Independent raw-output review and reproducible analysis artifacts

Completion requires conclusions that survive the prespecified robustness
checks and are reported with limitations and null results.

## Phase 13: Production Application

- Versioned backend API and persistent database
- Browser client with live state synchronization
- Authentication for paid features and secret isolation
- Background jobs, queues, retries, and concurrency controls
- Structured logging, metrics, health checks, and error reporting
- Containerization, CI, deployment, backups, and migration procedures

Completion requires a deployed staging environment, operational tests, and a
documented recovery procedure.

## Phase 14: Publication and Portfolio Package

- Full paper-style report with methods, results, robustness, and limitations
- Reproducible dataset and analysis package where licensing permits
- Architecture diagrams and experiment provenance
- Recorded product demonstration and technical walkthrough
- Portfolio case study explaining decisions, failures, and findings

Completion requires another person to reproduce the documented results from
the released materials.

## Definition of v2.0 Complete

Mind-Virus v2.0 is complete only when it is persistent, autonomous,
configuration-driven, experimentally robust, deployed, observable, and
reproducible. Until every criterion above is satisfied, it remains an active
research platform rather than a finished full-scale system.
