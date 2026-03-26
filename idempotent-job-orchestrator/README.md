# Idempotent Job Orchestrator

A production-leaning orchestration service that models the kinds of operational concerns senior backend teams care about: idempotent writes, retry scheduling, explicit state transitions, and durable persistence.

## Core Capabilities

- Idempotent job submission via `idempotency_key`
- Explicit lifecycle management for `queued`, `running`, `retry_pending`, `succeeded`, and `failed`
- Retry scheduling with bounded retries and backoff windows
- SQLite-backed persistence for deterministic local execution
- Filterable listing and operational stats endpoints

## API Surface

- `POST /v1/jobs`
- `GET /v1/jobs`
- `GET /v1/jobs/stats`
- `GET /v1/jobs/{job_id}`
- `POST /v1/jobs/{job_id}/dispatch`
- `POST /v1/jobs/{job_id}/complete`
- `POST /v1/jobs/{job_id}/fail`

## Local Run

```powershell
cd idempotent-job-orchestrator
pip install -e .[dev]
uvicorn orchestrator.main:app --reload
```

## Test

```powershell
cd idempotent-job-orchestrator
pytest -q
```
