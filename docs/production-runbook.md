# Mind-Virus Production Runbook

## Staging launch

Set `MIND_VIRUS_ACCESS_TOKEN` to a long random value, then run
`docker compose up --build -d`. Verify the service with
`http://localhost:8000/api/v1/health` and require a healthy container before
promotion. Provider credentials remain server-side and are added only when
live AI mode is intentionally enabled.

For public staging, deploy `render.yaml` as a Render Blueprint. It creates one
Docker web service in Frankfurt, waits for CI checks before auto-deployment,
generates the application access token, mounts a 1 GB disk at `/app/results`,
and gates deployment on `/api/v1/health`. Because persistent disks require a
paid Render web service, confirm the displayed monthly price before applying
the Blueprint.

## Database migrations

SQLite migrations run transactionally at startup using `PRAGMA user_version`.
The current schema is version 2. Never replace a database with a lower schema
version without restoring a verified backup.

## Backup and recovery

Use `ProductionStore.backup()` while the service is running; SQLite's backup
API creates a transactionally consistent copy. Restore into a new path with
`ProductionStore.restore()`, check `/api/v1/health`, then switch the volume or
database path. Do not overwrite the only production database during a drill.

Run the safe automated drill with:

```powershell
python -m scripts.validate_phase13_recovery
```

The drill creates temporary data, backs it up, restores it separately, checks
the schema, and verifies exact state equality.

## Incident recovery

1. Stop mutation traffic and preserve the failed volume.
2. Copy the latest verified backup into a new volume.
3. Start one staging instance against the restored copy.
4. Verify health, schema version, current state, logs, and metrics.
5. Resume traffic only after the state and audit records are confirmed.
