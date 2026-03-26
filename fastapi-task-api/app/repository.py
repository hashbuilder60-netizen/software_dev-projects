import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime

from .db import TaskDatabase
from .models import Task


@dataclass(slots=True)
class TaskFilters:
    status: str = "all"
    priority: str | None = None
    query: str | None = None
    limit: int = 20
    offset: int = 0


class TaskRepository:
    def __init__(self, database: TaskDatabase) -> None:
        self.database = database

    def list_tasks(self, filters: TaskFilters) -> tuple[list[Task], int]:
        where_clauses: list[str] = []
        parameters: list[object] = []

        if filters.status == "open":
            where_clauses.append("is_done = 0")
        elif filters.status == "done":
            where_clauses.append("is_done = 1")

        if filters.priority:
            where_clauses.append("priority = ?")
            parameters.append(filters.priority)

        if filters.query:
            where_clauses.append("(LOWER(title) LIKE ? OR LOWER(description) LIKE ?)")
            search = f"%{filters.query.lower()}%"
            parameters.extend([search, search])

        where = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

        with self.database.connect() as connection:
            total = int(
                connection.execute(
                    f"SELECT COUNT(*) FROM tasks {where}",
                    tuple(parameters),
                ).fetchone()[0]
            )
            rows = connection.execute(
                f"""
                SELECT *
                FROM tasks
                {where}
                ORDER BY created_at DESC, id DESC
                LIMIT ? OFFSET ?
                """,
                tuple([*parameters, filters.limit, filters.offset]),
            ).fetchall()

        return [self._to_task(row) for row in rows], total

    def get_task(self, task_id: int) -> Task | None:
        with self.database.connect() as connection:
            row = connection.execute(
                "SELECT * FROM tasks WHERE id = ?",
                (task_id,),
            ).fetchone()
        return self._to_task(row) if row else None

    def create_task(self, title: str, description: str, priority: str) -> Task:
        now = self._timestamp()
        with self.database.connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO tasks(title, description, priority, created_at, updated_at)
                VALUES(?, ?, ?, ?, ?)
                """,
                (title, description, priority, now, now),
            )
            task_id = int(cursor.lastrowid)
        task = self.get_task(task_id)
        if task is None:
            raise RuntimeError("Task creation failed.")
        return task

    def update_task(self, task_id: int, changes: dict[str, object]) -> Task | None:
        existing = self.get_task(task_id)
        if existing is None:
            return None

        now = self._timestamp()
        is_done = bool(changes.get("is_done", existing.is_done))
        completed_at = existing.completed_at
        if is_done and not existing.is_done:
            completed_at = datetime.now(UTC)
        elif not is_done:
            completed_at = None

        with self.database.connect() as connection:
            connection.execute(
                """
                UPDATE tasks
                SET title = ?, description = ?, priority = ?, is_done = ?, updated_at = ?, completed_at = ?
                WHERE id = ?
                """,
                (
                    str(changes.get("title", existing.title)),
                    str(changes.get("description", existing.description)),
                    str(changes.get("priority", existing.priority)),
                    int(is_done),
                    now,
                    completed_at.isoformat(timespec="seconds") if completed_at else None,
                    task_id,
                ),
            )
        return self.get_task(task_id)

    def delete_task(self, task_id: int) -> bool:
        with self.database.connect() as connection:
            cursor = connection.execute(
                "DELETE FROM tasks WHERE id = ?",
                (task_id,),
            )
        return cursor.rowcount > 0

    def stats(self) -> dict[str, object]:
        with self.database.connect() as connection:
            total = self._scalar(connection, "SELECT COUNT(*) FROM tasks")
            done = self._scalar(connection, "SELECT COUNT(*) FROM tasks WHERE is_done = 1")
            priority_rows = connection.execute(
                """
                SELECT priority, COUNT(*) AS count
                FROM tasks
                WHERE is_done = 0
                GROUP BY priority
                """
            ).fetchall()

        open_by_priority = {"low": 0, "medium": 0, "high": 0}
        for row in priority_rows:
            open_by_priority[str(row["priority"])] = int(row["count"])

        return {
            "total": total,
            "open": total - done,
            "done": done,
            "open_by_priority": open_by_priority,
        }

    @staticmethod
    def _scalar(connection: sqlite3.Connection, query: str) -> int:
        return int(connection.execute(query).fetchone()[0])

    @staticmethod
    def _timestamp() -> str:
        return datetime.now(UTC).isoformat(timespec="seconds")

    @staticmethod
    def _to_task(row: sqlite3.Row) -> Task:
        return Task(
            id=int(row["id"]),
            title=str(row["title"]),
            description=str(row["description"]),
            priority=str(row["priority"]),
            is_done=bool(row["is_done"]),
            created_at=datetime.fromisoformat(str(row["created_at"])),
            updated_at=datetime.fromisoformat(str(row["updated_at"])),
            completed_at=datetime.fromisoformat(str(row["completed_at"])) if row["completed_at"] else None,
        )
