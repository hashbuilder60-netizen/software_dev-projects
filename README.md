# Software Dev Projects

A multi-project repository showcasing practical software engineering work across CLI tooling and backend API development.

## Projects

### 1) Dev Journal CLI
Path: `dev-journal-cli/`

A lightweight command-line task journal for developers.

Highlights:
- SQLite-backed task storage
- Priority and tag support
- Commands for add/list/done/delete/stats
- Unit tests + GitHub Actions CI

Quick start:
```powershell
cd dev-journal-cli
pip install -e .
dev-journal add "Ship first feature" --priority high --tags backend
```

### 2) FastAPI Task API
Path: `fastapi-task-api/`

A clean REST API for task management using FastAPI.

Highlights:
- Health endpoint
- Task CRUD endpoints
- Request/response validation with Pydantic
- API tests + GitHub Actions CI

Quick start:
```powershell
cd fastapi-task-api
pip install -e .[dev]
uvicorn app.main:app --reload
```

## Repository Goals

- Show real project structure and maintainability
- Demonstrate testing and CI practices
- Build portfolio-ready software projects that can grow over time

## CI Workflows

- `dev-journal-cli/.github/workflows/ci.yml`
- `.github/workflows/fastapi-task-api-ci.yml`

## Author

Created by [hashbuilder60-netizen](https://github.com/hashbuilder60-netizen)