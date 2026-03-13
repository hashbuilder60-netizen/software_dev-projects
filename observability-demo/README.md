# Observability Demo

FastAPI demo for:
- structured logging
- Prometheus metrics
- Sentry error monitoring

## Run

```powershell
cd observability-demo
pip install -e .
observability-demo
```

Optional Sentry:
```powershell
$env:SENTRY_DSN="your-dsn"
observability-demo
```

Endpoints:
- `/health`
- `/metrics`
- `/boom` (intentional error)