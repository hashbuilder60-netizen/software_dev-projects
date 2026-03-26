from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from .models import JobCreate
from .repository import JobRepository


class ConflictError(Exception):
    pass


@dataclass(slots=True)
class RequestContext:
    actor: str
    request_id: str


class JobService:
    def __init__(self, repository: JobRepository) -> None:
        self.repository = repository

    def submit_job(self, payload: JobCreate, context: RequestContext):
        existing = self.repository.get_by_idempotency_key(payload.idempotency_key)
        if existing is not None:
            self._record_event(
                existing.id,
                "job.deduplicated",
                context,
                {"state": existing.state, "revision": existing.revision},
            )
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
        self._record_event(
            created.id,
            "job.created",
            context,
            {"state": created.state, "revision": created.revision},
        )
        return created, True

    def list_jobs(self, *, state: str | None, priority: str | None, limit: int, offset: int):
        return self.repository.list_jobs(state=state, priority=priority, limit=limit, offset=offset)

    def get_job(self, job_id: str):
        return self.repository.get_job(job_id)

    def dispatch_job(self, job_id: str, context: RequestContext):
        job = self._require_job(job_id)
        if job.state not in {"queued", "retry_pending"}:
            raise ConflictError(f"Job in state '{job.state}' cannot be dispatched.")
        if job.state == "retry_pending" and job.next_run_at and job.next_run_at > datetime.now(UTC):
            raise ConflictError("Retry window has not opened yet.")
        updated = self.repository.update_job(
            job_id,
            state="running",
            revision=job.revision + 1,
            attempts=job.attempts,
            updated_at=self._timestamp(),
            error_message=None,
            next_run_at=None,
        )
        self._record_event(
            job_id,
            "job.dispatched",
            context,
            {"from_state": job.state, "to_state": "running", "revision": updated.revision},
        )
        return updated

    def complete_job(self, job_id: str, context: RequestContext):
        job = self._require_job(job_id)
        if job.state != "running":
            raise ConflictError(f"Job in state '{job.state}' cannot be completed.")
        updated = self.repository.update_job(
            job_id,
            state="succeeded",
            revision=job.revision + 1,
            attempts=job.attempts,
            updated_at=self._timestamp(),
            error_message=None,
            next_run_at=None,
        )
        self._record_event(
            job_id,
            "job.completed",
            context,
            {"from_state": "running", "to_state": "succeeded", "revision": updated.revision},
        )
        return updated

    def fail_job(self, job_id: str, error_message: str, context: RequestContext):
        job = self._require_job(job_id)
        if job.state not in {"queued", "running", "retry_pending"}:
            raise ConflictError(f"Job in state '{job.state}' cannot transition to failed.")

        attempts = job.attempts + 1
        if attempts <= job.max_retries:
            next_run_at = datetime.now(UTC) + timedelta(seconds=job.backoff_seconds * attempts)
            updated = self.repository.update_job(
                job_id,
                state="retry_pending",
                revision=job.revision + 1,
                attempts=attempts,
                updated_at=self._timestamp(),
                error_message=error_message.strip(),
                next_run_at=next_run_at.isoformat(timespec="seconds"),
            )
            self._record_event(
                job_id,
                "job.retry_scheduled",
                context,
                {
                    "from_state": job.state,
                    "to_state": "retry_pending",
                    "attempts": attempts,
                    "revision": updated.revision,
                },
            )
            return updated

        updated = self.repository.update_job(
            job_id,
            state="failed",
            revision=job.revision + 1,
            attempts=attempts,
            updated_at=self._timestamp(),
            error_message=error_message.strip(),
            next_run_at=None,
        )
        self._record_event(
            job_id,
            "job.failed",
            context,
            {"from_state": job.state, "to_state": "failed", "attempts": attempts, "revision": updated.revision},
        )
        return updated

    def stats(self):
        return self.repository.stats()

    def list_audit_events(self, *, job_id: str | None, limit: int):
        return self.repository.list_audit_events(job_id=job_id, limit=limit)

    def _require_job(self, job_id: str):
        job = self.repository.get_job(job_id)
        if job is None:
            raise LookupError("Job not found.")
        return job

    def _record_event(
        self,
        job_id: str,
        event_type: str,
        context: RequestContext,
        metadata: dict[str, object],
    ) -> None:
        self.repository.record_audit_event(
            job_id=job_id,
            event_type=event_type,
            actor=context.actor,
            request_id=context.request_id,
            metadata=metadata,
            created_at=self._timestamp(),
        )

    @staticmethod
    def _timestamp() -> str:
        return datetime.now(UTC).isoformat(timespec="seconds")
