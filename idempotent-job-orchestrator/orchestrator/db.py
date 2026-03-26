import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


class OrchestratorDatabase:
    def __init__(self, db_path: str | Path) -> None:
        self.db_path = str(db_path)

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()

    def initialize(self) -> None:
        with self.connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS jobs (
                    id TEXT PRIMARY KEY,
                    job_type TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    idempotency_key TEXT NOT NULL UNIQUE,
                    priority TEXT NOT NULL,
                    state TEXT NOT NULL,
                    attempts INTEGER NOT NULL,
                    max_retries INTEGER NOT NULL,
                    backoff_seconds INTEGER NOT NULL,
                    error_message TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    next_run_at TEXT
                )
                """
            )
