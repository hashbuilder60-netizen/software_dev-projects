from datetime import UTC, datetime, timedelta
from uuid import uuid4

from .models import JobCreate
from .repository import JobRepository


class ConflictError(Exception):
    pass


class JobService:
    def __init__(self, repository: JobRepository) -> None:
        self.repository = repository

    def submit_job(self, payload: JobCreate):
        existing = self.repository.get_by_idempotency_key(payload.idempotency_key)
        if existing is not None:
            return existing, False

        now = self._timestamp()
        created = self.repository.create_job(
            job_id=str(uuid4()),
            job_type=payload.job_type.strip(),
            payload=payload.payload,
            idempotency_key=payload.idempotency_key.strip(),
            priority=payload.priority,
            max_retries=payload.max_retries,
            backoff_seconds=payload.backoff_seconds,
            created_at=now,
        )
        return created, True

    def list_jobs(self, *, state: str | None, priority: str | None, limit: int, offset: int):
        return self.repository.list_jobs(state=state, priority=priority, limit=limit, offset=offset)

    def get_job(self, job_id: str):
        return self.repository.get_job(job_id)

    def dispatch_job(self, job_id: str):
        job = self._require_job(job_id)
        if job.state not in {"queued", "retry_pending"}:
            raise ConflictError(f"Job in state '{job.state}' cannot be dispatched.")
        if job.state == "retry_pending" and job.next_run_at and job.next_run_at > datetime.now(UTC):
            raise ConflictError("Retry window has not opened yet.")
        return self.repository.update_job(
            job_id,
            state="running",
            attempts=job.attempts,
            updated_at=self._timestamp(),
            error_message=None,
            next_run_at=None,
        )

    def complete_job(self, job_id: str):
        job = self._require_job(job_id)
        if job.state != "running":
            raise ConflictError(f"Job in state '{job.state}' cannot be completed.")
        return self.repository.update_job(
            job_id,
            state="succeeded",
            attempts=job.attempts,
            updated_at=self._timestamp(),
            error_message=None,
            next_run_at=None,
        )

    def fail_job(self, job_id: str, error_message: str):
        job = self._require_job(job_id)
        if job.state not in {"queued", "running", "retry_pending"}:
            raise ConflictError(f"Job in state '{job.state}' cannot transition to failed.")

        attempts = job.attempts + 1
        if attempts <= job.max_retries:
            next_run_at = datetime.now(UTC) + timedelta(seconds=job.backoff_seconds * attempts)
            return self.repository.update_job(
                job_id,
                state="retry_pending",
                attempts=attempts,
                updated_at=self._timestamp(),
                error_message=error_message.strip(),
                next_run_at=next_run_at.isoformat(timespec="seconds"),
            )

        return self.repository.update_job(
            job_id,
            state="failed",
            attempts=attempts,
            updated_at=self._timestamp(),
            error_message=error_message.strip(),
            next_run_at=None,
        )

    def stats(self):
        return self.repository.stats()

    def _require_job(self, job_id: str):
        job = self.repository.get_job(job_id)
        if job is None:
            raise LookupError("Job not found.")
        return job

    @staticmethod
    def _timestamp() -> str:
        return datetime.now(UTC).isoformat(timespec="seconds")
