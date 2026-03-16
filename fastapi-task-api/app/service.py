from .models import TaskCreate, TaskUpdate
from .repository import TaskFilters, TaskRepository


class TaskService:
    def __init__(self, repository: TaskRepository) -> None:
        self.repository = repository

    def list_tasks(
        self,
        *,
        status: str,
        priority: str | None,
        query: str | None,
        limit: int,
        offset: int,
    ) -> tuple[list, int]:
        filters = TaskFilters(
            status=status,
            priority=priority,
            query=query.strip() if query else None,
            limit=limit,
            offset=offset,
        )
        return self.repository.list_tasks(filters)

    def get_task(self, task_id: int):
        return self.repository.get_task(task_id)

    def create_task(self, payload: TaskCreate):
        title = payload.title.strip()
        description = payload.description.strip()
        if not title:
            raise ValueError("Title cannot be empty.")
        return self.repository.create_task(title, description, payload.priority)

    def update_task(self, task_id: int, payload: TaskUpdate):
        changes = payload.model_dump(exclude_unset=True)
        if not changes:
            raise ValueError("At least one field must be provided.")

        if "title" in changes:
            if changes["title"] is None:
                raise ValueError("Title cannot be null.")
            title = str(changes["title"]).strip()
            if not title:
                raise ValueError("Title cannot be empty.")
            changes["title"] = title

        if "description" in changes:
            if changes["description"] is None:
                raise ValueError("Description cannot be null.")
            changes["description"] = str(changes["description"]).strip()

        if "priority" in changes and changes["priority"] is None:
            raise ValueError("Priority cannot be null.")

        if "is_done" in changes and changes["is_done"] is None:
            raise ValueError("is_done cannot be null.")

        return self.repository.update_task(task_id, changes)

    def delete_task(self, task_id: int) -> bool:
        return self.repository.delete_task(task_id)

    def stats(self):
        return self.repository.stats()
