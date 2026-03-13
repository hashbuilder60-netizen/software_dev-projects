# Dev Journal CLI

`Dev Journal` is a simple command-line project tracker designed for software developers.
It stores tasks in SQLite, supports priorities and tags, and gives you quick statistics.

## Features

- Add tasks with optional tags and priorities
- List open tasks or all tasks
- Mark tasks as completed
- Delete tasks
- View dashboard-style stats
- Zero external runtime dependencies

## Quick Start

1. Create and activate a virtual environment:
   - Windows PowerShell:
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```
2. Install in editable mode:
   ```powershell
   pip install -e .
   ```
3. Start using it:
   ```powershell
   dev-journal add "Set up CI pipeline" --priority high --tags backend,devops
   dev-journal list
   dev-journal done 1
   dev-journal stats
   ```

## CLI Commands

```text
dev-journal add "Task title" [--priority low|medium|high] [--tags tag1,tag2]
dev-journal list [--all]
dev-journal done <task-id>
dev-journal delete <task-id>
dev-journal stats
```

## Example Output

```text
ID  Status  Priority  Tags              Title
1   OPEN    HIGH      backend,devops    Set up CI pipeline
2   OPEN    MEDIUM    docs              Write README examples
```

## Run Tests

```powershell
python -m pytest -q
```

## Project Structure

```text
software_dev-projects/
  src/dev_journal/
    cli.py
    models.py
    service.py
    storage.py
  tests/
    test_service.py
  .github/workflows/ci.yml
  pyproject.toml
```