import logging
import os
import time
from fastapi import FastAPI
from prometheus_client import Counter, Histogram, generate_latest
from sentry_sdk import init as sentry_init
from sentry_sdk.integrations.fastapi import FastApiIntegration
from starlette.responses import Response

if os.getenv("SENTRY_DSN"):
    sentry_init(dsn=os.getenv("SENTRY_DSN"), traces_sample_rate=1.0, integrations=[FastApiIntegration()])

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("obs-demo")
REQUEST_COUNT = Counter("http_requests_total", "Total HTTP requests", ["path"])
REQUEST_LATENCY = Histogram("http_request_duration_seconds", "Request latency", ["path"])

app = FastAPI(title="Observability Demo")


@app.get("/health")
def health() -> dict[str, str]:
    start = time.perf_counter()
    REQUEST_COUNT.labels(path="/health").inc()
    logger.info("health endpoint hit")
    REQUEST_LATENCY.labels(path="/health").observe(time.perf_counter() - start)
    return {"status": "ok"}


@app.get("/boom")
def boom() -> None:
    REQUEST_COUNT.labels(path="/boom").inc()
    raise RuntimeError("intentional demo exception")


@app.get("/metrics")
def metrics() -> Response:
    return Response(generate_latest(), media_type="text/plain")


def run() -> None:
    import uvicorn

    uvicorn.run("obs_demo.main:app", host="0.0.0.0", port=4200, reload=False)