# Project Structure

This workspace keeps runtime-critical paths stable. Do not move directories that
are referenced by startup scripts, deployment scripts, or cloud-in runbooks.

## Root Directory

Keep only project entrypoints and top-level operational records in the root:

```text
README.md
AGENTS.md
DEPLOY_LOG.md
.env
.env.example
start-all.sh
stop-all.sh
platform/
deploy/
scripts/
systems-under-test/
runtime/
docs/
tests/
ai-gateway/
arex-jdbc-plugin/
```

## Runtime-Critical Directories

Do not move these without updating scripts and runbooks:

```text
platform/              Main recording playback platform
deploy/intranet/       Cloud-in offline deployment files
scripts/               Packaging, test, and helper scripts
systems-under-test/    Demo systems such as didi, loan-jar, loan-system
runtime/               Local generated packages, logs, backups, deployment records
```

## Documentation

Use these locations:

```text
docs/                  User-facing manuals and runbooks
docs/reports/          Analysis reports and comparison reports
DEPLOY_LOG.md          Canonical cloud-in deployment history; keep in project root
```

## Logs And Generated Files

Use these locations:

```text
runtime/logs/          Runtime logs and pid files
runtime/logs/archive/  One-off or misplaced old logs
runtime/mysql-backups/ MySQL backup dumps
runtime/intranet-incremental-packages/  Cloud-out packages to transfer inward
runtime/deployment-records/             Cloud-in deployment state records
```

## Rules

- Do not move `.env`, `start-all.sh`, `stop-all.sh`, `DEPLOY_LOG.md`, `platform/`,
  `deploy/`, `systems-under-test/`, `scripts/`, or `runtime/` just for tidiness.
- Reports from the root should go to `docs/reports/`.
- Accidental root logs should go to `runtime/logs/archive/`.
- Cloud-in deployment history must be appended to `DEPLOY_LOG.md`; detailed
  machine records should be linked from that file.
