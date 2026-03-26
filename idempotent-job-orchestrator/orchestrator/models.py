from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

JobState = Literal["queued", "running", "retry_pending", "succeeded", "failed"]
JobPriority = Literal["low", "standard", "high", "critical"]


class JobCreate(BaseModel):
    job_type: str = Field(min_length=3, max_length=80)
    payload: dict[str, Any] = Field(default_factory=dict)
    idempotency_key: str = Field(min_length=8, max_length=120)
    priority: JobPriority = "standard"
    max_retries: int = Field(default=3, ge=0, le=10)
    backoff_seconds: int = Field(default=30, ge=1, le=3600)


class JobFailRequest(BaseModel):
    error_message: str = Field(min_length=1, max_length=500)


class Job(BaseModel):
    id: str
    job_type: str
    payload: dict[str, Any]
    idempotency_key: str
    priority: JobPriority
    state: JobState
    revision: int
    attempts: int
    max_retries: int
    backoff_seconds: int
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime
    next_run_at: datetime | None = None


class JobSubmissionResponse(BaseModel):
    created: bool
    job: Job


class JobListResponse(BaseModel):
    items: list[Job]
    total: int
    limit: int
    offset: int


class JobStats(BaseModel):
    total: int
    queued: int
    running: int
    retry_pending: int
    succeeded: int
    failed: int


class AuditEvent(BaseModel):
    id: int
    job_id: str
    event_type: str
    actor: str
    request_id: str
    metadata: dict[str, Any]
    created_at: datetime


class AuditEventListResponse(BaseModel):
    items: list[AuditEvent]
    total: int
