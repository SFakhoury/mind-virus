# Portfolio Case Study: Mind-Virus

## Project at a glance

| Item | Evidence |
| --- | --- |
| Role | Creator and research engineer |
| Domain | Generative agents, misinformation, experimental AI |
| Core stack | Python, structured LLM outputs, JavaScript, SQLite, Docker |
| Research scale | 120 condition-trials plus a 648-decision robustness study |
| Quality | 389 automated tests at publication-report completion |
| Production | Containerized public staging on Render with CI and persistence |
| Reproducibility | Frozen datasets, protocol fingerprint, SHA-256 hashes, offline analysis |
| Public demo | [Mind-Virus Research Town](https://mind-virus-staging.onrender.com) |

## The problem

Most misinformation simulations treat propagation as a single event: if an
agent repeats a message, the model assumes that the agent believes it. That
assumption makes it impossible to represent an important real distinction—a
person or agent can discuss a rumor while doubting or rejecting it.

I built Mind-Virus to test a more precise question: can evidence-seeking
skepticism change what AI agents believe, what they repeat, or both?

## What I built

Mind-Virus is an end-to-end generative-agent research platform, not just a
single prompt or chat demonstration. It includes:

- residents with personalities, roles, private memories, plans, and social
  relationships;
- scored retrieval and listener-specific interpretation;
- separate state transitions for hearing, remembering, believing, and
  repeating a claim;
- claim identifiers, transmission generations, and lineage tracking;
- deterministic simulation and explicitly gated live-model modes;
- configuration-driven matched experiments with checkpointed collection;
- statistical analysis, figures, frozen protocols, and reproducible datasets;
- an animated browser town connected to the Python simulation; and
- production persistence, authentication, queues, metrics, CI, containers,
  backups, and recovery validation.

## The hardest decisions

### Separating belief from transmission

The central architecture decision was to avoid equating memory with belief or
repetition with acceptance. A listener produces a structured decision that
records its remembered version of the claim, belief status, repetition status,
confidence, and explanation. This separation made the research question
measurable and produced the project's most important finding.

### Making experiments matched and resumable

Hosted models are variable and paid calls can be interrupted. Baseline and
skeptical conditions therefore share trial and claim identifiers, while
treatment assignment and network configuration are seeded. Every completed
call is checkpointed, so an interrupted collection resumes without silently
duplicating observations or spending the budget twice.

### Keeping the public demo safe and inexpensive

The deployed town runs in deterministic mode and makes no OpenAI calls. Live
model execution is server-side, opt-in, authenticated in production, and
protected by call, token, and cost ceilings. Provider credentials are never
sent to the browser.

## Failures that improved the project

### The first experiment could not stop propagation

An early implementation forced each listener to pass the claim forward. It
could measure paraphrasing but could never answer whether skepticism stopped a
chain. I replaced forced transmission with an explicit repeat-or-stop decision
and updated the outcomes accordingly.

### Early dialogue confused knowledge and attribution

Pilot dialogue sometimes blurred who said what and allowed unsupported details
to appear. The system moved to explicit speaker/listener fields, structured
responses, role-aware evidence, grounding validation, rejected-output logging,
and retry behavior.

### Browser-owned time broke the shared world

When each open browser advanced the town independently, two viewers could
double the simulation speed and a closed browser could freeze it. I moved the
authoritative clock to the server. Multiple clients now observe one persistent
world, and the clock continues without a viewer.

### Production restarts exposed persistence gaps

Local execution hid startup and restart behavior that appeared during Render
deployment. Recovery validation led to schema-versioned storage, startup state
loading, persistent disks, backups, and a documented disaster-recovery path.

## Research results

The original confirmatory experiment used three claims, 20 matched trials per
condition and claim, 120 condition-trials, and 360 model calls. Skepticism did
not reduce exposure or maximum propagation depth, but pooled belief decreased
from 0.161 to 0.067—a paired difference of -0.094 with a diagnostic 95%
bootstrap interval of [-0.150, -0.044].

A later frozen robustness protocol crossed three claims, two models, two prompt
variants, and two conditions with 27 matched trials per cell. Across 648 live
decisions, repetition decreased from 0.830 to 0.000 and belief decreased from
0.117 to 0.000 under the tested skeptical intervention.

The responsible conclusion is conditional: evidence-seeking instructions can
reduce belief and can reduce repetition in these simulations, but the size and
channel of the effect depend on the treatment, prompt, model, claim, and study
design. The project does not claim to model human belief directly.

## Engineering evidence

- The full automated suite passed with 389 tests when the paper-style report
  was completed.
- GitHub Actions validates the Python suite and production container.
- The public service exposes health and operational metrics.
- State survived an actual Render restart during production validation.
- Two browser clients observed one server-owned clock without doubling it.
- Unauthorized paid/job routes returned HTTP 401.
- Deterministic public staging reported zero model calls, tokens, and cost.
- A valid authenticated background job completed successfully with no queue
  failures.

See [Phase 13 Production Validation](phase13-production-validation.md) for the
recorded acceptance evidence.

## Reproducible research evidence

The repository publishes the selected confirmatory datasets rather than every
temporary runtime file. Every published dataset has a SHA-256 checksum. A
single offline command validates those hashes, recomputes the analyses, and
compares the output with the published reports:

```powershell
python -m scripts.reproduce_publication
```

The reproduction path requires no API key and makes no paid request. The code
uses the MIT License; research materials use CC BY 4.0; citation metadata is
provided through `CITATION.cff`.

## Skills demonstrated

- Translating an ambiguous research question into measurable outcomes
- Multi-agent and memory-system architecture
- Structured model integration and grounding safeguards
- Controlled experiment design and matched statistical analysis
- Cost-aware and resumable model-data collection
- Test-driven debugging across 14 development phases
- Full-stack visualization and client/server synchronization
- Authentication, persistence, observability, CI/CD, and container deployment
- Reproducible research packaging and technical communication

## What I would do next

The strongest next research step is independent replication. That includes new
models and providers, larger and less linear social networks, more varied and
higher-stakes claims, blinded human review of belief and repetition labels,
and preregistration outside the repository before data collection. Those
extensions would test whether the observed effects survive beyond the current
prompted simulation environment.

## Links

- [Live research town](https://mind-virus-staging.onrender.com)
- [Full research report](research-report.md)
- [Architecture](architecture.md)
- [Experiment provenance](experiment-provenance.md)
- [Reproduction package](../publication/README.md)
- [Source repository](https://github.com/SFakhoury/mind-virus)
