import sqlite3
from datetime import datetime
from pathlib import Path

from dev_journal.models import Task


class TaskStorage:
    def __init__(self, db_path: str | Path = "tasks.db") -> None:
        self.db_path = str(db_path)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _initialize(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    tags TEXT NOT NULL DEFAULT '',
                    is_done INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    completed_at TEXT
                )
                """
            )

    def add_task(self, title: str, priority: str, tags: str) -> int:
        created_at = datetime.utcnow().isoformat(timespec="seconds")
        with self._connect() as conn:
            cursor = conn.execute(
                "INSERT INTO tasks(title, priority, tags, created_at) VALUES(?, ?, ?, ?)",
                (title, priority, tags, created_at),
            )
            return int(cursor.lastrowid)

    def list_tasks(self, include_done: bool = False) -> list[Task]:
        query = "SELECT * FROM tasks"
        params: tuple[()] | tuple[int]
        if not include_done:
            query += " WHERE is_done = ?"
            params = (0,)
        else:
            params = ()
        query += " ORDER BY is_done ASC, created_at ASC, id ASC"

        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
            return [self._to_task(row) for row in rows]

    def mark_done(self, task_id: int) -> bool:
        completed_at = datetime.utcnow().isoformat(timespec="seconds")
        with self._connect() as conn:
            cursor = conn.execute(
                "UPDATE tasks SET is_done = 1, completed_at = ? WHERE id = ? AND is_done = 0",
                (completed_at, task_id),
            )
            return cursor.rowcount > 0

    def delete_task(self, task_id: int) -> bool:
        with self._connect() as conn:
            cursor = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            return cursor.rowcount > 0

    def stats(self) -> dict[str, int]:
        with self._connect() as conn:
            total = self._scalar(conn, "SELECT COUNT(*) FROM tasks")
            done = self._scalar(conn, "SELECT COUNT(*) FROM tasks WHERE is_done = 1")
            open_tasks = total - done
            high = self._scalar(
                conn,
                "SELECT COUNT(*) FROM tasks WHERE is_done = 0 AND priority = 'high'",
            )
            return {"total": total, "open": open_tasks, "done": done, "high_priority_open": high}

    @staticmethod
    def _scalar(conn: sqlite3.Connection, query: str) -> int:
        return int(conn.execute(query).fetchone()[0])

    @staticmethod
    def _to_task(row: sqlite3.Row) -> Task:
        completed_at = datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None
        return Task(
            task_id=int(row["id"]),
            title=str(row["title"]),
            priority=str(row["priority"]),
            tags=str(row["tags"]),
            is_done=bool(row["is_done"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            completed_at=completed_at,
        )