from pathlib import Path

from dev_journal.service import TaskService
from dev_journal.storage import TaskStorage


def make_service(db_path: Path) -> TaskService:
    return TaskService(TaskStorage(db_path))


def test_create_and_list_tasks(tmp_path: Path) -> None:
    service = make_service(tmp_path / "tasks.db")
    task_id = service.create_task("Implement auth", priority="high", tags="backend,security")

    tasks = service.list_tasks()
    assert task_id == 1
    assert len(tasks) == 1
    assert tasks[0].title == "Implement auth"
    assert tasks[0].priority == "high"
    assert tasks[0].tags == "backend,security"
    assert tasks[0].is_done is False


def test_complete_task(tmp_path: Path) -> None:
    service = make_service(tmp_path / "tasks.db")
    task_id = service.create_task("Write docs")

    assert service.complete_task(task_id) is True
    assert service.complete_task(task_id) is False

    open_tasks = service.list_tasks()
    all_tasks = service.list_tasks(include_done=True)
    assert len(open_tasks) == 0
    assert len(all_tasks) == 1
    assert all_tasks[0].is_done is True


def test_delete_task(tmp_path: Path) -> None:
    service = make_service(tmp_path / "tasks.db")
    task_id = service.create_task("Refactor parser")
    assert service.remove_task(task_id) is True
    assert service.remove_task(task_id) is False
    assert service.list_tasks(include_done=True) == []


def test_stats(tmp_path: Path) -> None:
    service = make_service(tmp_path / "tasks.db")
    first = service.create_task("Setup project", priority="high")
    service.create_task("Add unit tests", priority="medium")
    service.complete_task(first)

    stats = service.get_stats()
    assert stats["total"] == 2
    assert stats["done"] == 1
    assert stats["open"] == 1
    assert stats["high_priority_open"] == 0