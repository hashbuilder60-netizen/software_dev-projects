from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class Task:
    task_id: int
    title: str
    priority: str
    tags: str
    is_done: bool
    created_at: datetime
    completed_at: datetime | None