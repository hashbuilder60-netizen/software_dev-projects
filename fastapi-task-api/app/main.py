import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal

from fastapi import Depends, FastAPI, HTTPException, Query, Request, status

from .db import TaskDatabase
from .models import Task, TaskCreate, TaskListResponse, TaskStats, TaskUpdate
from .repository import TaskRepository
from .service import TaskService


def get_service(request: Request) -> TaskService:
    return request.app.state.task_service


def create_app(db_path: str | Path | None = None) -> FastAPI:
    database = TaskDatabase(db_path or os.getenv("FASTAPI_TASK_API_DB_PATH", "tasks.db"))
    service = TaskService(TaskRepository(database))

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        database.initialize()
        yield

    app = FastAPI(
        title="FastAPI Task API",
        version="0.2.0",
        description="Layered FastAPI task service with filtering, stats, and SQLite persistence.",
        lifespan=lifespan,
    )
    app.state.task_service = service

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "storage": "sqlite"}

    @app.get("/tasks", response_model=TaskListResponse)
    def list_tasks(
        status_filter: Literal["open", "done", "all"] = Query(default="all", alias="status"),
        priority: Literal["low", "medium", "high"] | None = Query(default=None),
        q: str | None = Query(default=None, max_length=120),
        limit: int = Query(default=20, ge=1, le=100),
        offset: int = Query(default=0, ge=0),
        task_service: TaskService = Depends(get_service),
    ) -> TaskListResponse:
        items, total = task_service.list_tasks(
            status=status_filter,
            priority=priority,
            query=q,
            limit=limit,
            offset=offset,
        )
        return TaskListResponse(items=items, total=total, limit=limit, offset=offset)

    @app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
    def create_task(payload: TaskCreate, task_service: TaskService = Depends(get_service)) -> Task:
        try:
            return task_service.create_task(payload)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/tasks/stats", response_model=TaskStats)
    def task_stats(task_service: TaskService = Depends(get_service)) -> TaskStats:
        return TaskStats(**task_service.stats())

    @app.get("/tasks/{task_id}", response_model=Task)
    def get_task(task_id: int, task_service: TaskService = Depends(get_service)) -> Task:
        task = task_service.get_task(task_id)
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found.")
        return task

    @app.patch("/tasks/{task_id}", response_model=Task)
    def update_task(
        task_id: int,
        payload: TaskUpdate,
        task_service: TaskService = Depends(get_service),
    ) -> Task:
        try:
            updated = task_service.update_task(task_id, payload)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        if updated is None:
            raise HTTPException(status_code=404, detail="Task not found.")
        return updated

    @app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
    def delete_task(task_id: int, task_service: TaskService = Depends(get_service)) -> None:
        deleted = task_service.delete_task(task_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Task not found.")

    return app


app = create_app()
