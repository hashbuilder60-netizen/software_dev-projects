import json
import sqlite3
from datetime import datetime

from .db import OrchestratorDatabase
from .models import Job


class JobRepository:
    def __init__(self, database: OrchestratorDatabase) -> None:
        self.database = database

    def create_job(
        self,
        *,
        job_id: str,
        job_type: str,
        payload: dict,
        idempotency_key: str,
        priority: str,
        max_retries: int,
        backoff_seconds: int,
        created_at: str,
    ) -> Job:
        with self.database.connect() as connection:
            connection.execute(
                """
                INSERT INTO jobs(
                    id, job_type, payload, idempotency_key, priority, state,
                    attempts, max_retries, backoff_seconds, created_at, updated_at
                )
                VALUES(?, ?, ?, ?, ?, 'queued', 0, ?, ?, ?, ?)
                """,
                (
                    job_id,
                    job_type,
                    json.dumps(payload, sort_keys=True),
                    idempotency_key,
                    priority,
                    max_retries,
                    backoff_seconds,
                    created_at,
                    created_at,
                ),
            )
        job = self.get_job(job_id)
        if job is None:
            raise RuntimeError("Persisted job could not be reloaded.")
        return job

    def get_by_idempotency_key(self, idempotency_key: str) -> Job | None:
        with self.database.connect() as connection:
            row = connection.execute(
                "SELECT * FROM jobs WHERE idempotency_key = ?",
                (idempotency_key,),
            ).fetchone()
        return self._to_job(row) if row else None

    def get_job(self, job_id: str) -> Job | None:
        with self.database.connect() as connection:
            row = connection.execute(
                "SELECT * FROM jobs WHERE id = ?",
                (job_id,),
            ).fetchone()
        return self._to_job(row) if row else None

    def list_jobs(
        self,
        *,
        state: str | None,
        priority: str | None,
        limit: int,
        offset: int,
    ) -> tuple[list[Job], int]:
        where_clauses: list[str] = []
        parameters: list[object] = []

        if state:
            where_clauses.append("state = ?")
            parameters.append(state)
        if priority:
            where_clauses.append("priority = ?")
            parameters.append(priority)

        where = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

        with self.database.connect() as connection:
            total = int(
                connection.execute(
                    f"SELECT COUNT(*) FROM jobs {where}",
                    tuple(parameters),
                ).fetchone()[0]
            )
            rows = connection.execute(
                f"""
                SELECT *
                FROM jobs
                {where}
                ORDER BY created_at DESC, id DESC
                LIMIT ? OFFSET ?
                """,
                tuple([*parameters, limit, offset]),
            ).fetchall()
        return [self._to_job(row) for row in rows], total

    def update_job(
        self,
        job_id: str,
        *,
        state: str,
        attempts: int,
        updated_at: str,
        error_message: str | None,
        next_run_at: str | None,
    ) -> Job | None:
        with self.database.connect() as connection:
            cursor = connection.execute(
                """
                UPDATE jobs
                SET state = ?, attempts = ?, updated_at = ?, error_message = ?, next_run_at = ?
                WHERE id = ?
                """,
                (state, attempts, updated_at, error_message, next_run_at, job_id),
            )
        if cursor.rowcount == 0:
            return None
        return self.get_job(job_id)

    def stats(self) -> dict[str, int]:
        with self.database.connect() as connection:
            rows = connection.execute(
                "SELECT state, COUNT(*) AS count FROM jobs GROUP BY state"
            ).fetchall()

        counts = {
            "total": 0,
            "queued": 0,
            "running": 0,
            "retry_pending": 0,
            "succeeded": 0,
            "failed": 0,
        }
        for row in rows:
            state = str(row["state"])
            count = int(row["count"])
            counts[state] = count
            counts["total"] += count
        return counts

    @staticmethod
    def _to_job(row: sqlite3.Row) -> Job:
        return Job(
            id=str(row["id"]),
            job_type=str(row["job_type"]),
            payload=json.loads(str(row["payload"])),
            idempotency_key=str(row["idempotency_key"]),
            priority=str(row["priority"]),
            state=str(row["state"]),
            attempts=int(row["attempts"]),
            max_retries=int(row["max_retries"]),
            backoff_seconds=int(row["backoff_seconds"]),
            error_message=str(row["error_message"]) if row["error_message"] else None,
            created_at=datetime.fromisoformat(str(row["created_at"])),
            updated_at=datetime.fromisoformat(str(row["updated_at"])),
            next_run_at=datetime.fromisoformat(str(row["next_run_at"])) if row["next_run_at"] else None,
        )
