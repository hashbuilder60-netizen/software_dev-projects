# Idempotent Job Orchestrator

The flagship backend service in this portfolio. It is deliberately positioned around the kinds of concerns that push a project beyond CRUD: authenticated control-plane access, idempotent writes, explicit lifecycle transitions, revisioned state, auditability, retry windows, metrics, and containerized execution.

## Why It Matters

- `X-API-Key` protected control-plane endpoints
- Idempotent submission via `idempotency_key`
- Durable SQLite persistence with schema migration support
- Revisioned jobs so state changes are explicitly traceable
- Audit event stream for lifecycle transitions and duplicate submissions
- Prometheus-compatible `/metrics` endpoint
- Dockerfile and `docker-compose.yml` for repeatable local execution

## API Surface

- `GET /health`
- `GET /metrics`
- `POST /v1/jobs`
- `GET /v1/jobs`
- `GET /v1/jobs/stats`
- `GET /v1/jobs/{job_id}`
- `GET /v1/audit-events`
- `POST /v1/jobs/{job_id}/dispatch`
- `POST /v1/jobs/{job_id}/complete`
- `POST /v1/jobs/{job_id}/fail`

## Local Run

```powershell
cd idempotent-job-orchestrator
pip install -e .[dev]
$env:IDEMPOTENT_ORCHESTRATOR_API_KEY="dev-control-plane-key"
uvicorn orchestrator.main:app --reload
```

## Container Run

```powershell
cd idempotent-job-orchestrator
docker compose up --build
```

## Test

```powershell
cd idempotent-job-orchestrator
pytest -q
```
