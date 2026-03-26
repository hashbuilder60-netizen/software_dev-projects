# FastAPI Task API

A layered FastAPI service with SQLite persistence, filtering, pagination, task stats, and endpoint tests.

## Features

- App factory for testable app creation
- SQLite-backed persistence with repository/service layers
- Task creation, fetch, update, delete, and stats endpoints
- Filtering by status, priority, search query, limit, and offset
- Richer task model with description, priority, timestamps, and completion tracking

## Endpoints

- `GET /health`
- `GET /tasks`
- `POST /tasks`
- `GET /tasks/stats`
- `GET /tasks/{task_id}`
- `PATCH /tasks/{task_id}`
- `DELETE /tasks/{task_id}`

## Example Query

```text
GET /tasks?status=open&priority=high&q=ship&limit=10&offset=0
```

## Local Run

```powershell
cd fastapi-task-api
pip install -e .[dev]
uvicorn app.main:app --reload
```

## Run Tests

```powershell
cd fastapi-task-api
pytest -q
```
