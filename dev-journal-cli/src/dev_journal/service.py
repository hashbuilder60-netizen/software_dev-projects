from dev_journal.storage import TaskStorage


VALID_PRIORITIES = {"low", "medium", "high"}


class TaskService:
    def __init__(self, storage: TaskStorage) -> None:
        self.storage = storage

    def create_task(self, title: str, priority: str = "medium", tags: str = "") -> int:
        clean_title = title.strip()
        clean_priority = priority.strip().lower()
        clean_tags = ",".join(tag.strip().lower() for tag in tags.split(",") if tag.strip())

        if not clean_title:
            raise ValueError("Task title cannot be empty.")
        if clean_priority not in VALID_PRIORITIES:
            valid = ", ".join(sorted(VALID_PRIORITIES))
            raise ValueError(f"Priority must be one of: {valid}.")

        return self.storage.add_task(clean_title, clean_priority, clean_tags)

    def list_tasks(self, include_done: bool = False):
        return self.storage.list_tasks(include_done=include_done)

    def complete_task(self, task_id: int) -> bool:
        return self.storage.mark_done(task_id)

    def remove_task(self, task_id: int) -> bool:
        return self.storage.delete_task(task_id)

    def get_stats(self) -> dict[str, int]:
        return self.storage.stats()