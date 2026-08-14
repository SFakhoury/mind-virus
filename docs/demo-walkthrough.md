# Mind-Virus Product Demo and Technical Walkthrough

This is the recording plan for a five-to-seven-minute portfolio demonstration.
It uses the deterministic public town, makes no OpenAI API calls, and does not
display credentials or private dashboards.

## Before recording

1. Open the [public research town](https://mind-virus-staging.onrender.com) and
   wait until the residents and clock are visible.
2. Open these repository pages in separate browser tabs:
   - the project README;
   - `docs/research-report.md`;
   - `docs/architecture.md`;
   - `docs/portfolio-case-study.md`; and
   - `publication/README.md`.
3. Close email, messaging, billing, API-key, environment-variable, and Render
   settings pages.
4. Hide bookmarks or notifications that reveal personal information.
5. Use a 1920x1080 recording area when possible and increase browser zoom
   enough for text to remain readable.
6. Confirm that the public town reports zero API calls and zero estimated cost.

## Recording script

### Scene 1 — The question (about 40 seconds)

**Show:** The README title, research question, and town screenshot.

**Say:**

> Mind-Virus is a generative-agent research platform that studies how
> unverified claims move through a society of memory-driven AI agents. The key
> idea is that hearing, remembering, repeating, and believing a claim are four
> different events. I built the project to test whether evidence-seeking
> skepticism changes what agents transmit, what they believe, or both.

### Scene 2 — The live town (about 75 seconds)

**Show:** The public town. Let the clock advance and residents move. Point to
the resident activities and conversation transcript. Pause and resume once.

**Say:**

> This is the deployed deterministic research town. Each resident has a role,
> private memory, needs, activities, plans, and relationships. The Python
> server owns the authoritative clock and world state, so multiple viewers
> observe the same persistent simulation instead of advancing separate worlds.
> The public demo intentionally uses deterministic cognition. It demonstrates
> the complete application without exposing a provider key or generating API
> costs. Live model-backed collection is a separate, explicitly gated mode.

### Scene 3 — Agent and system architecture (about 70 seconds)

**Show:** The diagrams in `docs/architecture.md`.

**Say:**

> Incoming observations and dialogue enter a resident's private memory stream.
> Relevant memories are retrieved and used for listener-specific
> interpretation. A structured decision then records whether the resident
> believes and whether it repeats the claim. Claim identity and transmission
> lineage are preserved even when wording changes. Around that research core,
> the production system adds SQLite persistence, an event journal,
> authentication, background jobs, cost safeguards, health checks, metrics,
> containers, continuous integration, and backup recovery.

### Scene 4 — What went wrong and what changed (about 60 seconds)

**Show:** The “Failures that improved the project” section of the portfolio
case study.

**Say:**

> The first version forced every listener to pass the rumor forward, which
> meant it could never test whether skepticism stopped propagation. I replaced
> that with an explicit repeat-or-stop decision and separated belief from
> transmission. Pilot dialogue also exposed attribution and invented-evidence
> problems, leading to structured speaker and listener fields, grounding
> validation, rejected-output logging, and retries. Later, deployment revealed
> that a browser-owned clock could freeze or run twice as fast, so the clock
> moved to the persistent server-owned world.

### Scene 5 — Research results (about 90 seconds)

**Show:** The abstract and result tables in `docs/research-report.md`, followed
by the two belief figures.

**Say:**

> The original confirmatory experiment contained 120 condition-trials and 360
> model calls. Skepticism did not reduce exposure or maximum propagation depth,
> but pooled belief decreased from 0.161 to 0.067. That showed why belief and
> repetition must be measured separately. A later frozen robustness study
> collected 648 live decisions across three claims, two models, two prompt
> variants, and two conditions. Under that stronger intervention, repetition
> decreased from 0.830 to zero, and belief decreased from 0.117 to zero. These
> are conditional findings about the tested model simulations, not claims about
> human communities.

### Scene 6 — Reproducibility and engineering quality (about 70 seconds)

**Show:** `publication/README.md`, `CITATION.cff`, the license links, and the
latest successful GitHub Actions run. Optionally show terminal output from
`python -m scripts.reproduce_publication`.

**Say:**

> The publication package includes frozen datasets, a protocol fingerprint,
> SHA-256 integrity hashes, analysis code, reports, licenses, and citation
> metadata. A fresh clone can reproduce the published statistics offline with
> one command and no API key. The project also has a large automated test suite,
> container validation, and recorded production acceptance evidence covering
> persistence, authentication, queues, observability, backups, and restart
> recovery.

### Scene 7 — Close (about 30 seconds)

**Show:** The town and the project links in the README.

**Say:**

> Mind-Virus combines multi-agent AI, controlled experimentation, statistical
> analysis, full-stack visualization, and production engineering. The main
> research lesson is simple: information can travel without being believed,
> and an intervention must be evaluated against both outcomes. The live demo,
> source code, research report, and reproduction package are linked here.

## Recording acceptance checklist

The Phase 14 demo is complete only when the published recording satisfies all
of these checks:

- [ ] Duration is approximately five to seven minutes.
- [ ] The live town visibly advances and residents move.
- [ ] Zero public-demo API usage is visible or clearly stated.
- [ ] The belief-versus-repetition distinction is explained.
- [ ] Both confirmatory stages and their sample sizes are shown.
- [ ] Limitations and the non-human scope are stated.
- [ ] Architecture and reproducibility are demonstrated.
- [ ] No API key, access token, billing detail, email, or private dashboard is
      visible.
- [ ] Speech is understandable and on-screen text is readable at 1080p.
- [ ] The final video URL is added to the README and this document.

## Technical walkthrough backup

If the public deployment is temporarily restarting, record the deterministic
town locally:

```powershell
python -m scripts.run_town_ui
```

Then open `http://127.0.0.1:8000`. Do not add `--live`; the walkthrough does
not require a model call.

## Publication placeholders

- **Video URL:** Add after upload.
- **Recording date:** Add after recording.
- **Demo commit:** Add the Git commit shown in the published repository at the
  time of recording.
