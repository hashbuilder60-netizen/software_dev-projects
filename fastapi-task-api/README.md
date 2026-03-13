# FastAPI Task API

Simple task API for portfolio/demo use.

## Endpoints

- `GET /health` - service health check
- `GET /tasks` - list tasks
- `POST /tasks` - create task
- `PATCH /tasks/{task_id}` - update completion status
- `DELETE /tasks/{task_id}` - delete task

## Local Run

```powershell
cd fastapi-task-api
pip install -e .
uvicorn app.main:app --reload
```

## Run Tests

```powershell
cd fastapi-task-api
pip install -e .[dev]
pytest -q
```