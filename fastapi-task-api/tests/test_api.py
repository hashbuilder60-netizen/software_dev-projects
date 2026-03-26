from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client(tmp_path: Path) -> TestClient:
    app = create_app(tmp_path / "tasks.db")
    with TestClient(app) as test_client:
        yield test_client


def test_health(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "storage": "sqlite"}


def test_task_lifecycle(client: TestClient) -> None:
    create_response = client.post(
        "/tasks",
        json={"title": "Ship MVP", "description": "Release the first beta", "priority": "high"},
    )
    assert create_response.status_code == 201
    task = create_response.json()
    assert task["title"] == "Ship MVP"
    assert task["description"] == "Release the first beta"
    assert task["priority"] == "high"
    task_id = task["id"]

    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == task_id

    update_response = client.patch(
        f"/tasks/{task_id}",
        json={"is_done": True, "description": "Release completed"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["is_done"] is True
    assert update_response.json()["completed_at"] is not None

    delete_response = client.delete(f"/tasks/{task_id}")
    assert delete_response.status_code == 204
    assert client.get(f"/tasks/{task_id}").status_code == 404


def test_list_filters_pagination_and_stats(client: TestClient) -> None:
    client.post("/tasks", json={"title": "Ship docs", "priority": "high"})
    client.post("/tasks", json={"title": "Refactor auth", "priority": "medium"})
    third = client.post(
        "/tasks",
        json={"title": "Ship dashboard", "description": "frontend polish", "priority": "high"},
    ).json()
    client.patch(f"/tasks/{third['id']}", json={"is_done": True})

    filtered = client.get("/tasks", params={"status": "open", "priority": "high", "q": "ship"})
    assert filtered.status_code == 200
    body = filtered.json()
    assert body["total"] == 1
    assert len(body["items"]) == 1
    assert body["items"][0]["title"] == "Ship docs"

    paged = client.get("/tasks", params={"limit": 1, "offset": 1})
    assert paged.status_code == 200
    assert paged.json()["limit"] == 1
    assert paged.json()["offset"] == 1

    stats = client.get("/tasks/stats")
    assert stats.status_code == 200
    assert stats.json()["total"] == 3
    assert stats.json()["done"] == 1
    assert stats.json()["open"] == 2
    assert stats.json()["open_by_priority"]["high"] == 1


def test_validation_and_404_cases(client: TestClient) -> None:
    bad_create = client.post("/tasks", json={"title": "   "})
    assert bad_create.status_code == 400

    empty_update = client.patch("/tasks/1", json={})
    assert empty_update.status_code == 400

    null_update = client.patch("/tasks/1", json={"is_done": None})
    assert null_update.status_code == 400

    update_response = client.patch("/tasks/999", json={"is_done": True})
    assert update_response.status_code == 404

    delete_response = client.delete("/tasks/999")
    assert delete_response.status_code == 404
