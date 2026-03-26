import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from .db import OrchestratorDatabase
from .models import Job, JobCreate, JobFailRequest, JobListResponse, JobStats, JobSubmissionResponse
from .repository import JobRepository
from .service import ConflictError, JobService


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

    def get_service() -> JobService:
        return app.state.job_service

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "idempotent-job-orchestrator"}

    @app.post("/v1/jobs", response_model=JobSubmissionResponse)
    def submit_job(payload: JobCreate, job_service: JobService = Depends(get_service)):
        job, created = job_service.submit_job(payload)
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
    ) -> JobListResponse:
        items, total = job_service.list_jobs(state=state, priority=priority, limit=limit, offset=offset)
        return JobListResponse(items=items, total=total, limit=limit, offset=offset)

    @app.get("/v1/jobs/stats", response_model=JobStats)
    def stats(job_service: JobService = Depends(get_service)) -> JobStats:
        return JobStats(**job_service.stats())

    @app.get("/v1/jobs/{job_id}", response_model=Job)
    def get_job(job_id: str, job_service: JobService = Depends(get_service)) -> Job:
        job = job_service.get_job(job_id)
        if job is None:
            raise HTTPException(status_code=404, detail="Job not found.")
        return job

    @app.post("/v1/jobs/{job_id}/dispatch", response_model=Job)
    def dispatch_job(job_id: str, job_service: JobService = Depends(get_service)) -> Job:
        try:
            job = job_service.dispatch_job(job_id)
        except LookupError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ConflictError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        return job

    @app.post("/v1/jobs/{job_id}/complete", response_model=Job)
    def complete_job(job_id: str, job_service: JobService = Depends(get_service)) -> Job:
        try:
            job = job_service.complete_job(job_id)
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
    ) -> Job:
        try:
            job = job_service.fail_job(job_id, payload.error_message)
        except LookupError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ConflictError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        return job

    return app


app = create_app()
