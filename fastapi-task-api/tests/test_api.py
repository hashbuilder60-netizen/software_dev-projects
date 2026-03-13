from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_task_lifecycle() -> None:
    create_response = client.post("/tasks", json={"title": "Ship MVP"})
    assert create_response.status_code == 201
    task = create_response.json()
    assert task["title"] == "Ship MVP"
    task_id = task["id"]

    list_response = client.get("/tasks")
    assert list_response.status_code == 200
    assert any(t["id"] == task_id for t in list_response.json())

    update_response = client.patch(f"/tasks/{task_id}", json={"is_done": True})
    assert update_response.status_code == 200
    assert update_response.json()["is_done"] is True

    delete_response = client.delete(f"/tasks/{task_id}")
    assert delete_response.status_code == 204


def test_404_cases() -> None:
    update_response = client.patch("/tasks/999", json={"is_done": True})
    assert update_response.status_code == 404

    delete_response = client.delete("/tasks/999")
    assert delete_response.status_code == 404