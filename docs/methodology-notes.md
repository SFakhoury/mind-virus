# Methodology Notes

This document records important experimental decisions, pilot findings,
methodological corrections, and known limitations in Mind-Virus.

The purpose is to preserve the reasoning behind the system's design and
distinguish engineering demonstrations from research evidence.

## Research Question

> Does skepticism measurably slow or reduce the propagation of a false
> belief through a society of memory-driven AI agents?

The project treats hearing, remembering, believing, and repeating a claim
as separate processes.

## Development and Validation Stages

### Deterministic Prototype

The initial experiment framework used deterministic thresholds and seeded
randomness. This verified storage, retrieval, claim lineage, belief state,
logging, and matched experimental conditions without spending API credit.

These deterministic results validate software behavior only. They are not
evidence about model-backed agent behavior.

### Model-Backed Interpretation Pilot

A live propagation chain tested whether different agent personalities could
produce listener-specific memories.

The model preserved attribution and uncertainty in most responses, while
the wording changed across generations. This established that natural
language mutation could be observed and recorded.

A single chain is an engineering demonstration, not a controlled experiment.

### Initial Controlled Pilot

The first live controlled pilot used five baseline and five skeptical
chains, with four agents per chain.

The diagnostic results were:

- Baseline average final lexical similarity: 0.332
- Skeptical average final lexical similarity: 0.282
- Baseline average final uncertainty signals: 1.80
- Skeptical average final uncertainty signals: 2.20
- Total model calls: 30

These values must not be interpreted as final findings. The trial count was
small, and the experiment still contained a major methodological flaw:
every listener was forced to repeat the claim.

## Problems Found During Piloting

### Forced Propagation

The original chain always passed the listener's interpreted memory to the
next agent.

This meant skepticism could change wording and uncertainty, but could not
reduce exposure or stop propagation. The design therefore could not answer
the primary research question.

#### Correction

The model-backed decision now separates:

1. What the listener remembers
2. Whether the listener believes the claim
3. Whether the listener repeats the claim
4. The listener's confidence
5. The reason for the decision

A propagation chain now stops when an agent chooses not to repeat a claim.

### Speaker Attribution Errors

One pilot response reversed or confused the identities of the speaker and
listener.

#### Correction

The model now receives explicit speaker and listener fields and returns a
validated structured response. Attribution will still be audited in saved
outputs because structured formatting cannot guarantee semantic accuracy.

### Lexical Similarity Is Limited

The current Jaccard word-overlap metric measures shared vocabulary.

It does not reliably detect:

- Paraphrases with the same meaning
- Negation
- Changes in certainty
- Attribution changes
- New unsupported details

#### Planned Correction

Later analysis will combine lexical metrics with semantic comparison and
manual review of a documented sample.

### Small Pilot Size

Five trials per condition are insufficient for strong conclusions.

#### Correction

Pilot results are labeled diagnostic. Final trial counts will be selected
after inspecting variance and estimating the number of observations needed
for a meaningful comparison.

### Prompt-Induced Treatment Effects

The skeptical condition explicitly describes agents as skeptical,
evidence-seeking, and careful with hearsay.

This is the experimental intervention, but wording may influence style as
well as belief and repetition decisions.

#### Mitigation

All non-treatment variables must remain matched across conditions. The
study will report the exact prompts and treat conclusions as specific to
the tested intervention wording.

### Model Variability

Hosted language-model output may change between requests and model
versions. A random seed does not guarantee exact reproduction of model
responses.

#### Mitigation

The project saves:

- Model identifier
- Experiment configuration
- Raw messages
- Structured decisions
- Trial and condition identifiers
- Usage information when available

Claims will be based on repeated aggregate behavior rather than exact
response reproduction.

### Estimated Versus Actual Cost

Early budget safeguards estimate token usage before running an experiment.

#### Planned Correction

Future model-backed runs will record actual input and output token usage
returned by the API and calculate observed cost alongside the pre-run
estimate.

## Current Interpretation Policy

A listener may:

- Remember and believe a claim
- Remember but reject a claim
- Remember a claim but refuse to repeat it
- Repeat a claim with uncertainty
- Repeat a transformed version
- Stop the propagation chain

Hearing alone never creates a belief automatically.

## Current Threats to Validity

The current experiment remains limited by:

- A linear chain rather than a dynamic social network
- One initial claim
- A small number of agent personalities
- Model and prompt dependence
- Basic mutation metrics
- Limited trial counts
- No independent human annotation yet
- No animated town or spatial scheduling yet

These limitations will be addressed where practical and reported where
they cannot be eliminated.

## Evidence Standard

Mind-Virus distinguishes three levels of output:

1. **Software validation** — automated tests show the code behaves as designed.
2. **Pilot evidence** — small runs identify flaws and estimate behavior.
3. **Research evidence** — repeated controlled trials support a measured
   comparison with uncertainty and limitations reported.

Only the third level will be used to answer the research question.
