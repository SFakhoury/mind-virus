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

**Status: complete.** Reproducible robustness manifests now cross model,
prompt, temperature, and repetition settings in randomized execution order,
with every cell tied to the frozen experiment specification.
Paired analyses now report raw effects, standardized Cohen's dz values, and
bootstrap intervals, while Benjamini-Hochberg adjustment controls false
discoveries across families of tested outcomes.
The measurement suite now quantifies claim mutation, confidence calibration,
exposure reach, propagation depth, unique transmission edges, and network-edge
coverage as distinct research outcomes.
Raw model outputs can now be randomized into blinded review packets with a
separate provenance key, dual-reviewer judgments, Cohen's kappa agreement,
and explicit disagreement lists for independent adjudication.
Robustness synthesis now reports direction consistency, supporting,
contradicting, and inconclusive cells, and only preserves a conclusion when it
meets its prespecified consistency threshold without significant reversals.
A resumable 32-call live pilot now compares Luna and Terra across neutral and
evidence-explicit prompts, baseline and skeptical listeners, with per-call
checkpoints, observed token accounting, and a $0.10 hard cost ceiling.
A separate resumable extension tests the same model, prompt, and intervention
matrix across three distinct claims before any larger confirmatory expansion.
A separate powered confirmatory protocol freezes 27 new trials per condition
and cell (648 structured decisions total), primary and secondary outcomes,
direction, alpha, power target, pricing assumptions, and a $1.50 ceiling.

- Multiple model families or versions
- Prompt and temperature sensitivity analysis
- Larger samples based on power and variance estimates
- Effect sizes, uncertainty intervals, multiple-comparison handling
- Mutation, calibration, belief, exposure, and network-level measurements
- Independent raw-output review and reproducible analysis artifacts

Completion requires conclusions that survive the prespecified robustness
checks and are reported with limitations and null results.

## Phase 13: Production Application

**Status: complete.** Production work adds a versioned v1 API,
SQLite-backed durable storage, and a database-aware health check while
preserving the prototype routes during migration. The server now atomically
persists its current town snapshot and exposes restart-safe retrieval through
the versioned API. Connected browsers now receive server-sent state events
and read-only polling, while one server-owned clock advances and persists the
authoritative world. The legacy manual tick route requires authentication in
production.
Production mode now requires a separate application access token for paid
mutation routes; the OpenAI provider key remains isolated on the server.
A bounded background queue now supports observable asynchronous work with
retries, while mutation locks prevent concurrent requests from racing shared
town and agent state.
Structured JSON logging redacts secrets, operational metrics expose uptime and
request/error counters, and health checks include database and queue status.
An unprivileged Docker image, persistent Compose volume, container health
check, and GitHub Actions test/build pipeline now validate every change.
Versioned startup migrations, transactionally consistent backups, isolated
restore validation, and an incident-recovery runbook are now implemented.
A Render Blueprint defines the public staging service, CI-gated deployment,
generated application secret, health gate, and persistent SQLite disk.
Public staging validation confirmed restart persistence, one-viewer and
multi-viewer clock consistency, protected mutation routes, observable queued
work, and zero model usage in deterministic mode. See
[phase13-production-validation.md](phase13-production-validation.md).

- Versioned backend API and persistent database
- Browser client with live state synchronization
- Authentication for paid features and secret isolation
- Background jobs, queues, retries, and concurrency controls
- Structured logging, metrics, health checks, and error reporting
- Containerization, CI, deployment, backups, and migration procedures

Completion criteria were satisfied on August 14, 2026 with a deployed staging
environment, operational tests, and a documented recovery procedure.

## Phase 14: Publication and Portfolio Package

**Status: in progress.**

- Full paper-style report with methods, results, robustness, and limitations **(complete)**
- Reproducible dataset and analysis package where licensing permits **(complete)**
- Architecture diagrams and experiment provenance **(complete)**
- Recorded product demonstration and technical walkthrough
- Portfolio case study explaining decisions, failures, and findings **(complete)**

Completion requires another person to reproduce the documented results from
the released materials.

## Definition of v2.0 Complete

Mind-Virus v2.0 is complete only when it is persistent, autonomous,
configuration-driven, experimentally robust, deployed, observable, and
reproducible. Until every criterion above is satisfied, it remains an active
research platform rather than a finished full-scale system.
