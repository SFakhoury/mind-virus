# Phase 13 Production Validation

## Scope

Phase 13 was validated against the public Render staging deployment on
August 14, 2026. The validated deployment used commit `5853632` and the
public deterministic configuration. No OpenAI API requests were made during
the operational validation.

Staging URL: <https://mind-virus-staging.onrender.com>

## Verified controls

| Control | Evidence | Result |
| --- | --- | --- |
| Deployment | Render deployed commit `5853632` successfully | Pass |
| Automated checks | GitHub Actions `test` and `container` jobs succeeded | Pass |
| Health gate | `/api/v1/health` returned status and database `ok`, schema version 2 | Pass |
| Durable state | Town time survived a complete Render service restart | Pass |
| Server-owned clock | With all browser tabs closed, 20 seconds advanced the town by 50 simulated minutes | Pass |
| Multiple viewers | Two simultaneous browser tabs advanced the town by the same 50 simulated minutes | Pass |
| Unauthorized job | Tokenless `POST /api/v1/jobs/step` returned HTTP 401 | Pass |
| Authorized job | A valid application token completed one deterministic job in one attempt | Pass |
| Manual tick protection | Tokenless `POST /api/world/tick` returned HTTP 401 | Pass |
| Queue health | One job completed and zero jobs failed | Pass |
| Model isolation | Usage remained at zero calls, zero tokens, and zero estimated model cost | Pass |

## Operational observations

The public staging service uses a single server-owned clock. Browsers observe
authoritative state through server-sent events and read-only polling; opening
additional viewers does not multiply simulation speed. The server saves the
world after each tick to the persistent disk mounted at `/app/results` and
loads that world during startup.

The public deployment intentionally runs deterministic simulation mode.
`OPENAI_API_KEY` is not required for this deployment, and live model-backed
execution remains disabled until separate rate limits and spending controls
are approved and configured.

## Cost boundary

Render displayed a recurring staging price of $7.25 per month at creation:
$7.00 for the Starter web service and $0.25 for its persistent disk. Provider
model usage is separate and remained zero throughout this validation.

## Conclusion

Phase 13 meets its completion criteria: a deployed staging environment,
operational verification, durable restart recovery, protected mutation
routes, observable background work, and a documented recovery procedure.
