from collections.abc import Iterable
from datetime import datetime, UTC

from .models import Task


class TaskStore:
    def __init__(self) -> None:
        self._tasks: dict[int, Task] = {}
        self._next_id = 1

    def list_tasks(self) -> list[Task]:
        return sorted(self._tasks.values(), key=lambda t: t.id)

    def create_task(self, title: str) -> Task:
        task = Task(id=self._next_id, title=title.strip(), is_done=False, created_at=datetime.now(UTC))
        self._tasks[self._next_id] = task
        self._next_id += 1
        return task

    def update_task(self, task_id: int, is_done: bool) -> Task | None:
        task = self._tasks.get(task_id)
        if task is None:
            return None
        updated = task.model_copy(update={"is_done": is_done})
        self._tasks[task_id] = updated
        return updated

    def delete_task(self, task_id: int) -> bool:
        return self._tasks.pop(task_id, None) is not None