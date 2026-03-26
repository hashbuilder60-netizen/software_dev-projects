from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

Priority = Literal["low", "medium", "high"]
TaskStatus = Literal["open", "done", "all"]


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    description: str = Field(default="", max_length=500)
    priority: Priority = "medium"


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=500)
    priority: Priority | None = None
    is_done: bool | None = None


class Task(BaseModel):
    id: int
    title: str
    description: str
    priority: Priority
    is_done: bool
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None = None


class TaskListResponse(BaseModel):
    items: list[Task]
    total: int
    limit: int
    offset: int


class TaskStats(BaseModel):
    total: int
    open: int
    done: int
    open_by_priority: dict[str, int]
