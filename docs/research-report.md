# Mind-Virus: Skepticism, Belief, and Misinformation Propagation in AI Agents

- **Author:** Sanad Samer Fakhoury
- **Project:** [SFakhoury/mind-virus](https://github.com/SFakhoury/mind-virus)
- **Research materials:** CC BY 4.0
- **Software:** MIT License

## Abstract

Mind-Virus is a controlled generative-agent research platform for examining
whether evidence-seeking skepticism changes how language-model agents transmit
and believe unverified claims. The system deliberately models hearing,
remembering, repeating, and believing as separate events. It combines private
agent memories, listener-specific interpretation, claim lineage, matched
experimental conditions, checkpointed model calls, statistical analysis, and
an interactive persistent town.

An initial confirmatory experiment contained 120 condition-trials and 360
model calls across three claims. Skepticism did not change exposure or maximum
propagation depth, but pooled belief decreased from 0.161 to 0.067 (paired
difference -0.094; diagnostic 95% bootstrap interval [-0.150, -0.044]). A
subsequent frozen robustness protocol tested three claims, two models, two
prompt variants, two conditions, and 27 matched trials per cell. Across 648
live decisions, repetition decreased from 0.830 to 0.000 (difference -0.830;
95% bootstrap interval [-0.870, -0.787]; exact paired p=2.108e-81), while
belief decreased from 0.117 to 0.000 (difference -0.117; interval [-0.154,
-0.083]; exact paired p=7.276e-12).

The studies show that conclusions depend materially on intervention design:
skepticism may alter internal acceptance without stopping transmission, but a
stronger, explicitly operationalized intervention can also suppress
repetition. These are findings about the tested model simulations and prompts,
not claims about human communities.

## 1. Research question

> Does skepticism measurably slow or reduce the spread of a false belief
> through a society of memory-driven AI agents?

This question has two distinct parts:

1. Does skepticism reduce how far an unverified claim travels?
2. Does skepticism reduce how often agents accept the claim as true?

Treating these as the same outcome would hide agents that discuss a rumor
while explicitly rejecting it.

## 2. System design

Each resident has a personality, role, private memory stream, retrieval
mechanism, belief state, and social context. Incoming dialogue creates a
memory attributed to its speaker. Relevant memories inform a structured
listener decision containing:

- the remembered message;
- whether the claim is believed;
- whether the claim is repeated;
- belief confidence;
- the reason for the decision; and
- the resulting transmission generation.

Claim identifiers and transmission lineage remain stable even when the text is
paraphrased. This makes it possible to track semantic descendants without
equating exact word overlap with identity. The implementation is described in
[Architecture](architecture.md).

## 3. Intervention and conditions

### 3.1 Baseline

Baseline agents use neutral role and personality instructions. They can
remember, evaluate, believe, reject, repeat, or stop a claim. They are not
described as gullible or instructed to produce a favorable control result.

### 3.2 Skeptical treatment

Treated agents receive an evidence-seeking instruction emphasizing the
difference between unsupported reports and established facts. All other
available design variables are matched across conditions. The robustness study
also crosses neutral and evidence-explicit prompt variants, allowing the
result to be examined across more than one instruction framing.

The treatment is a prompt-level behavioral intervention. It does not prove
that the model performs external fact-checking, and it should not be described
as a general-purpose misinformation defense.

## 4. Research development and corrections

Deterministic prototypes first validated memory, lineage, logging, and matched
conditions without consuming API credit. Live pilots then revealed several
methodological problems.

The earliest chain forced every listener to transmit the message. That design
could measure wording changes but could never show a chain stopping. It was
replaced by a structured choice separating memory, belief, and repetition.
Explicit speaker and listener fields were added after attribution errors were
observed. Later collection introduced call ceilings, token accounting,
checkpointing, treatment calibration, multiple claims, frozen protocols, and
paired analyses. Pilot outputs remained diagnostic and were excluded from the
frozen confirmatory datasets.

These corrections are not incidental debugging history: they explain why the
two confirmatory stages estimate different intervention behavior and why the
final platform records multiple outcomes separately.

## 5. Original confirmatory experiment

### 5.1 Design

The experiment used three everyday unverified claims:

- the bakery is giving away free bread;
- the library is closing early because of a pipe leak; and
- a bus route is changing because of road work.

For every claim there were 20 matched trials in each of two conditions,
producing 120 condition-trials and 360 model calls. Trial and claim identifiers
were matched across conditions. Effects are skeptical minus baseline; negative
values indicate a reduction under treatment.

The prespecified primary outcome was average exposed agents. Secondary
outcomes were maximum transmission generation, repetition rate, belief rate,
and belief confidence. Paired bootstrap intervals describe uncertainty across
the simulated matched trials.

### 5.2 Results

| Outcome | Baseline | Skeptical | Difference | Diagnostic 95% interval |
| --- | ---: | ---: | ---: | ---: |
| Exposed agents | 4.000 | 4.000 | +0.000 | [+0.000, +0.000] |
| Maximum generation | 3.000 | 3.000 | +0.000 | [+0.000, +0.000] |
| Repetition rate | 1.000 | 0.989 | -0.011 | [-0.028, +0.000] |
| Belief rate | 0.161 | 0.067 | -0.094 | [-0.150, -0.044] |

![Confirmatory belief rates](figures/confirmatory-belief-rates.png)

![Confirmatory belief effects](figures/confirmatory-belief-effects.png)

The intervention changed belief more strongly than transmission. The chains
still carried the claim to every resident, but fewer treated agents accepted
it. A propagation-only metric would therefore have missed the clearest effect.

## 6. Confirmatory robustness experiment

### 6.1 Frozen protocol

The robustness protocol was frozen before collection with fingerprint
`46282c7a2dbd5ae0e246a2e1a26d7515f02b5bddaae0740a3e085a13e66735c3`.
It specified:

- three claims;
- two model configurations (`gpt-5.6-luna` and `gpt-5.6-terra`);
- two prompt variants (`neutral` and `evidence_explicit`);
- baseline and skeptical conditions;
- 27 matched trials per condition in each cell;
- 12 claim/model/prompt cells and 648 planned decisions;
- repetition as the primary outcome;
- belief as the secondary outcome; and
- a two-sided alpha of 0.05 and target power of 0.80.

Every completed model decision was checkpointed. Collection completed all 648
records and cost an estimated $0.5439.

### 6.2 Analysis

Binary outcomes were compared within matched condition pairs. Reported
differences are skeptical minus baseline. Confidence intervals use 10,000
paired bootstrap samples with a fixed analysis seed. Exact McNemar tests use
the discordant pairs and test whether condition-specific binary outcomes are
symmetric.

### 6.3 Results

| Outcome | Baseline | Skeptical | Difference | 95% interval | Exact paired p |
| --- | ---: | ---: | ---: | ---: | ---: |
| Repetition | 0.830 | 0.000 | -0.830 | [-0.870, -0.787] | 2.108e-81 |
| Belief | 0.117 | 0.000 | -0.117 | [-0.154, -0.083] | 7.276e-12 |

Repetition decreased in all 12 claim/model/prompt cells. Belief effects were
more heterogeneous: three cells showed reductions and nine were tied at zero,
largely because both conditions already had zero belief in those cells. The
complete cell table is available in
[Phase 12 Confirmatory Robustness Results](phase12-confirmatory-robustness-results.md).

## 7. Synthesis

The original experiment rejected the simplest claim that skepticism always
stops exposure: the treatment lowered belief without materially reducing
transmission. The robustness experiment found a much larger repetition effect
under its stronger and more explicitly specified intervention.

These outcomes are not interchangeable replications. They show that treatment
wording, decision structure, model configuration, and ceiling or floor effects
can determine whether skepticism appears primarily as reduced belief or as
reduced transmission. The defensible conclusion is therefore conditional:
within these simulations, evidence-seeking instructions can reduce belief and
can reduce repetition, but the magnitude and behavioral channel depend on the
tested protocol.

## 8. Threats to validity

### Construct validity

Prompted model outputs are operational proxies for belief and repetition, not
human mental states. A structured `believes_claim` field measures the model's
task response under the prompt. It is not evidence of consciousness or an
internal belief comparable to a person's belief.

### Internal validity

The intervention itself can change response style as well as evidential
standards. Exact semantic compliance cannot be guaranteed by structured output
validation alone. Matched trials reduce variation from claims and trial setup,
but hosted model behavior can still vary between calls and deployments.

### External validity

The claims are low-stakes local rumors, the social environments are synthetic,
and the tested model and prompt configurations represent a narrow population.
Results should not be generalized to elections, health misinformation, large
social networks, other providers, or human communities without new evidence.

### Statistical limitations

The original experiment exhibited a transmission ceiling. The robustness
study exhibited a skeptical-condition floor. Very small p-values reflect the
consistency and size of paired differences in this finite simulated dataset;
they do not eliminate construct or external-validity concerns. Bootstrap
intervals quantify trial variation under the analysis procedure, not every
source of model or deployment uncertainty.

### Researcher and implementation dependence

The author designed the intervention, software, and analysis. There has not
yet been independent replication or blinded human annotation. The published
package enables such review but is not a substitute for it.

## 9. Engineering contribution

Beyond the empirical findings, Mind-Virus demonstrates an end-to-end research
engineering workflow:

- private memory-driven agents and autonomous social behavior;
- explicit separation of exposure, memory, repetition, and belief;
- configuration-driven matched experiments;
- resumable and cost-bounded live model collection;
- frozen protocols and dataset integrity hashes;
- paired statistical analysis and generated figures;
- a persistent, authenticated, observable production service; and
- an animated browser town for inspecting behavior.

The public staging site uses deterministic mode and makes no OpenAI requests.
It demonstrates the platform rather than reproducing a paid research run.

## 10. Reproducibility and data availability

The publication package contains the frozen 120-trial and 648-decision
datasets, original analysis output, licenses, and SHA-256 checksums. From a
fresh clone, run:

```powershell
python -m scripts.reproduce_publication
```

The command verifies dataset integrity, recomputes both analyses, compares the
outputs with the committed results, and makes no network or API requests. See
[Experiment Provenance](experiment-provenance.md) for the complete artifact
lineage.

Source code is available under the MIT License. Research data, documentation,
and figures are available under CC BY 4.0.

## 11. Conclusion

Mind-Virus provides evidence that misinformation transmission and belief
formation should not be treated as one variable in generative-agent research.
In one controlled design, skeptical treatment lowered belief without stopping
exposure. In a broader robustness design, a stronger skeptical intervention
also suppressed repetition across every tested cell. The results support
measuring both what agents transmit and what they accept, while underscoring
that observed effects remain conditional on the intervention, prompts, models,
claims, and simulated environment.
