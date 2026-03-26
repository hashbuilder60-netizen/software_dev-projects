import os
import time
from contextlib import asynccontextmanager
from pathlib import Path
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, Query, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, Response
from prometheus_client import Counter, Histogram, generate_latest

from .db import OrchestratorDatabase
from .models import (
    AuditEventListResponse,
    Job,
    JobCreate,
    JobFailRequest,
    JobListResponse,
    JobStats,
    JobSubmissionResponse,
)
from .repository import JobRepository
from .service import ConflictError, JobService, RequestContext

REQUEST_COUNT = Counter(
    "idempotent_orchestrator_http_requests_total",
    "Total HTTP requests processed by the orchestrator",
    ["path", "method", "status"],
)
REQUEST_LATENCY = Histogram(
    "idempotent_orchestrator_http_request_duration_seconds",
    "HTTP request latency for the orchestrator",
    ["path", "method"],
)


def create_app(db_path: str | Path | None = None) -> FastAPI:
    database = OrchestratorDatabase(db_path or os.getenv("IDEMPOTENT_ORCHESTRATOR_DB_PATH", "jobs.db"))
    service = JobService(JobRepository(database))

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        database.initialize()
        app.state.job_service = service
        yield

    app = FastAPI(
        title="Idempotent Job Orchestrator",
        version="0.1.0",
        description="Operational job orchestration with idempotent submission and retry scheduling.",
        lifespan=lifespan,
    )

    @app.middleware("http")
    async def add_request_context(request: Request, call_next):
        request_id = request.headers.get("X-Request-Id") or str(uuid4())
        request.state.request_id = request_id
        started = time.perf_counter()
        response = await call_next(request)
        duration = time.perf_counter() - started
        response.headers["X-Request-Id"] = request_id
        REQUEST_COUNT.labels(
            path=request.url.path,
            method=request.method,
            status=str(response.status_code),
        ).inc()
        REQUEST_LATENCY.labels(path=request.url.path, method=request.method).observe(duration)
        return response

    def get_service() -> JobService:
        return app.state.job_service

    def get_request_context(request: Request) -> RequestContext:
        expected_api_key = os.getenv("IDEMPOTENT_ORCHESTRATOR_API_KEY", "dev-control-plane-key")
        provided_api_key = request.headers.get("X-API-Key")
        if provided_api_key != expected_api_key:
            raise HTTPException(status_code=401, detail="Invalid or missing X-API-Key.")
        return RequestContext(actor="api-key", request_id=request.state.request_id)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "idempotent-job-orchestrator"}

    @app.get("/metrics")
    def metrics() -> Response:
        return Response(generate_latest(), media_type="text/plain")

    @app.post("/v1/jobs", response_model=JobSubmissionResponse)
    def submit_job(
        payload: JobCreate,
        job_service: JobService = Depends(get_service),
        context: RequestContext = Depends(get_request_context),
    ):
        job, created = job_service.submit_job(payload, context)
        response = JobSubmissionResponse(created=created, job=job)
        if created:
            return JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content=jsonable_encoder(response),
            )
        return response

    @app.get("/v1/jobs", response_model=JobListResponse)
    def list_jobs(
        state: str | None = Query(default=None),
        priority: str | None = Query(default=None),
        limit: int = Query(default=20, ge=1, le=100),
        offset: int = Query(default=0, ge=0),
        job_service: JobService = Depends(get_service),
        _context: RequestContext = Depends(get_request_context),
    ) -> JobListResponse:
        items, total = job_service.list_jobs(state=state, priority=priority, limit=limit, offset=offset)
        return JobListResponse(items=items, total=total, limit=limit, offset=offset)

    @app.get("/v1/jobs/stats", response_model=JobStats)
    def stats(
        job_service: JobService = Depends(get_service),
        _context: RequestContext = Depends(get_request_context),
    ) -> JobStats:
        return JobStats(**job_service.stats())

    @app.get("/v1/audit-events", response_model=AuditEventListResponse)
    def list_audit_events(
        job_id: str | None = Query(default=None),
        limit: int = Query(default=50, ge=1, le=200),
        job_service: JobService = Depends(get_service),
        _context: RequestContext = Depends(get_request_context),
    ) -> AuditEventListResponse:
        items, total = job_service.list_audit_events(job_id=job_id, limit=limit)
        return AuditEventListResponse(items=items, total=total)

    @app.get("/v1/jobs/{job_id}", response_model=Job)
    def get_job(
        job_id: str,
        job_service: JobService = Depends(get_service),
        _context: RequestContext = Depends(get_request_context),
    ) -> Job:
        job = job_service.get_job(job_id)
        if job is None:
            raise HTTPException(status_code=404, detail="Job not found.")
        return job

    @app.post("/v1/jobs/{job_id}/dispatch", response_model=Job)
    def dispatch_job(
        job_id: str,
        job_service: JobService = Depends(get_service),
        context: RequestContext = Depends(get_request_context),
    ) -> Job:
        try:
            job = job_service.dispatch_job(job_id, context)
        except LookupError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ConflictError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        return job

    @app.post("/v1/jobs/{job_id}/complete", response_model=Job)
    def complete_job(
        job_id: str,
        job_service: JobService = Depends(get_service),
        context: RequestContext = Depends(get_request_context),
    ) -> Job:
        try:
            job = job_service.complete_job(job_id, context)
        except LookupError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ConflictError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        return job

    @app.post("/v1/jobs/{job_id}/fail", response_model=Job)
    def fail_job(
        job_id: str,
        payload: JobFailRequest,
        job_service: JobService = Depends(get_service),
        context: RequestContext = Depends(get_request_context),
    ) -> Job:
        try:
            job = job_service.fail_job(job_id, payload.error_message, context)
        except LookupError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ConflictError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        return job

    return app


app = create_app()
