# Exact Demo Rehearsal Guide

Use this guide to practise the entire Mind-Virus video before recording. Do
one complete rehearsal, take the requested screenshots, and review them before
starting the final recording.

## Part 1 — Prepare the browser

Open one normal browser window. Do not use a window containing API-key,
billing, email, Render environment, or private account pages.

Open these tabs in this exact order:

1. **Project home**  
   `https://github.com/SFakhoury/mind-virus`
2. **Live research town**  
   `https://mind-virus-staging.onrender.com`
3. **Architecture**  
   `https://github.com/SFakhoury/mind-virus/blob/main/docs/architecture.md`
4. **Portfolio case study**  
   `https://github.com/SFakhoury/mind-virus/blob/main/docs/portfolio-case-study.md`
5. **Research report**  
   `https://github.com/SFakhoury/mind-virus/blob/main/docs/research-report.md`
6. **Reproduction package**  
   `https://github.com/SFakhoury/mind-virus/blob/main/publication/README.md`
7. **Latest GitHub Actions runs**  
   `https://github.com/SFakhoury/mind-virus/actions`

Wait for every page to finish loading before rehearsing.

## Part 2 — Verify every scene before recording

### Check the project home

On tab 1:

1. Confirm that the Mind-Virus title and town screenshot appear.
2. Scroll until the research question is visible.
3. Scroll to Project Status and confirm the public staging link is present.
4. Return to the top so the tab is ready for Scene 1.

### Check the live town

On tab 2:

1. Wait until all four residents appear.
2. Write down the displayed day and time.
3. Wait approximately ten seconds and confirm that time advances.
4. Confirm that at least one resident changes position or activity.
5. Click **Pause** and confirm the browser animation pauses.
6. Click **Resume**.
7. Confirm the Live model usage panel shows `0` API calls and `$0.0000`.
8. Do not expect natural model-generated conversation here. The public site is
   intentionally deterministic and free.

### Check the architecture

On tab 3:

1. Confirm the System overview diagram renders.
2. Find the Agent cognition diagram.
3. Find the Experimental pipeline diagram.
4. Scroll back to System overview for the start of Scene 3.

### Check the project failures

On tab 4:

1. Find **Failures that improved the project**.
2. Confirm the forced-propagation, grounding, browser-clock, and restart
   sections are visible below it.
3. Leave the page at that heading for Scene 4.

### Check the research results

On tab 5:

1. Find the original confirmatory result table in Section 5.
2. Confirm the table shows 4.000 exposure in both conditions and belief rates
   of 0.161 and 0.067.
3. Scroll to Section 6 and confirm the robustness table shows repetition rates
   of 0.830 and 0.000.
4. Return to the first result table for the start of Scene 5.

### Check reproducibility and CI

On tab 6, confirm the three publication datasets and the offline reproduction
command are visible. On tab 7, confirm the latest workflow has green checks.
Never open workflow secrets, repository secrets, or environment settings while
recording.

## Part 3 — Rehearse the narration

1. Open `docs/demo-walkthrough.md` on a second device or print it. If you keep
   it on the recording computer, place it outside the captured area.
2. Read all seven scenes aloud once without recording.
3. Rehearse again while switching tabs at each scene heading.
4. Aim for five to seven minutes, but clarity matters more than exact length.
5. Pause briefly after each major result instead of rushing through numbers.
6. Do not improvise stronger scientific claims than the written script.

## Part 4 — Screenshots to send for review

Before recording, capture and send these four screenshots:

1. The full live town with all residents, the clock, and model usage visible.
2. The GitHub-rendered architecture diagrams.
3. The original and robustness result tables in the research report.
4. The latest green GitHub Actions run.

These screenshots confirm that the public pages are readable and that the
recording will not expose private information.

## Part 5 — Record only after rehearsal approval

Start recording with `Windows key + Alt + R`. Follow the seven scenes in
`docs/demo-walkthrough.md`. Stop with the same shortcut and save the result as
`mind-virus-product-demo.mp4`.

Do not commit the MP4 to Git. Upload it after review, then add its public or
unlisted URL to the README and the walkthrough document.
