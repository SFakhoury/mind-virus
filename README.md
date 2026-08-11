# Mind-Virus

**Mind-Virus** is an experimental generative-agent simulation designed to study how misinformation propagates through a society of memory-driven AI agents, how claims mutate during transmission, and whether skeptical agents can measurably reduce false-belief propagation.

The project is inspired by the architecture introduced in Stanford's *Generative Agents: Interactive Simulacra of Human Behavior*.

## Research Question

> **Does skepticism measurably slow or reduce the spread of a false belief through a society of memory-driven AI agents?**

## Core Idea

Each simulated agent has its own personality, private memory stream, retrieval mechanism, reflection process, conversation behavior, and attitude toward uncertain information.

A false claim is seeded into one agent's memory. From that point onward, there is no hard-coded rumor-spreading mechanism.

Instead, information propagates through memory retrieval, natural conversation, listener interpretation, and the formation of new memories.

## Experimental Intervention

Some agents can be configured as **skeptical**. These agents distinguish unsupported claims from established facts and require stronger evidence before accepting information as true.

The eventual controlled experiment compares a baseline society with no skeptical agents against a society containing a fixed proportion of skeptical agents.

## Architecture

Mind-Virus builds on three central concepts from the Generative Agents architecture:

1. **Memory** - agents maintain persistent streams of experiences.
2. **Retrieval** - relevant memories are selected using recency, importance, and semantic relevance.
3. **Reflection** - agents can synthesize experiences into higher-level conclusions.

The project extends this architecture with rumor lineage tracking, semantic mutation, belief confidence, transmission generations, skeptical behavior, and controlled multi-run experiments.

See [docs/architecture.md](docs/architecture.md) for the detailed architecture.

## Core Principle

> **Hearing a claim, remembering a claim, repeating a claim, and believing a claim are distinct processes.**

This distinction separates information exposure from actual belief formation.

## Project Status

**Current phase: Phase 1 - Core Agent Loop complete**

The core agent loop now supports private memories, scored retrieval, dialogue, and listener-specific interpretation.

## Documentation

- [Architecture](docs/architecture.md)
- [Research Foundations](docs/research-foundations.md)
- [References](docs/references.md)

## Planned Deliverables

- Working memory-driven multi-agent simulation
- Reproducible misinformation propagation experiments
- Multi-run experimental logs
- Controlled skeptical vs. non-skeptical comparison
- Quantitative visualizations
- Short research write-up

## Development Philosophy

Experimental claims will be based on repeated logged trials rather than individual LLM outputs.

The project prioritizes reproducibility, controlled comparisons, clear documentation, and minimal experimental confounds over unnecessary simulation complexity.

