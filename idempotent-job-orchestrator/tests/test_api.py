from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from orchestrator.main import create_app


@pytest.fixture
def client(tmp_path: Path) -> TestClient:
    app = create_app(tmp_path / "jobs.db")
    with TestClient(app) as test_client:
        yield test_client


def auth_headers(request_id: str = "test-request-id") -> dict[str, str]:
    return {
        "X-API-Key": "dev-control-plane-key",
        "X-Request-Id": request_id,
    }


def test_control_plane_requires_api_key(client: TestClient) -> None:
    response = client.get("/v1/jobs")
    assert response.status_code == 401


def test_idempotent_submission_returns_existing_job(client: TestClient) -> None:
    payload = {
        "job_type": "email-dispatch",
        "payload": {"user_id": 42},
        "idempotency_key": "tenant-a:job-001",
        "priority": "high",
        "max_retries": 2,
        "backoff_seconds": 1,
    }

    first = client.post("/v1/jobs", json=payload, headers=auth_headers("create-1"))
    second = client.post("/v1/jobs", json=payload, headers=auth_headers("create-2"))
    audit = client.get(
        "/v1/audit-events",
        params={"job_id": first.json()["job"]["id"]},
        headers=auth_headers("audit-read"),
    )

    assert first.status_code == 201
    assert first.json()["created"] is True
    assert first.json()["job"]["revision"] == 1
    assert second.status_code == 200
    assert second.json()["created"] is False
    assert first.json()["job"]["id"] == second.json()["job"]["id"]
    assert first.headers["X-Request-Id"] == "create-1"
    assert audit.status_code == 200
    assert audit.json()["total"] == 2


def test_dispatch_complete_flow(client: TestClient) -> None:
    created = client.post(
        "/v1/jobs",
        json={
            "job_type": "invoice-sync",
            "payload": {"invoice_id": "inv-1"},
            "idempotency_key": "billing:inv-1",
        },
        headers=auth_headers("dispatch-create"),
    ).json()["job"]

    dispatched = client.post(f"/v1/jobs/{created['id']}/dispatch", headers=auth_headers("dispatch"))
    completed = client.post(f"/v1/jobs/{created['id']}/complete", headers=auth_headers("complete"))
    audit = client.get(
        "/v1/audit-events",
        params={"job_id": created["id"]},
        headers=auth_headers("audit"),
    )

    assert dispatched.status_code == 200
    assert dispatched.json()["state"] == "running"
    assert dispatched.json()["revision"] == 2
    assert completed.status_code == 200
    assert completed.json()["state"] == "succeeded"
    assert completed.json()["revision"] == 3
    assert audit.status_code == 200
    assert audit.json()["total"] == 3


def test_retry_scheduling_and_failure_terminal_state(client: TestClient) -> None:
    created = client.post(
        "/v1/jobs",
        json={
            "job_type": "warehouse-rebuild",
            "payload": {"tenant": "core"},
            "idempotency_key": "analytics:warehouse-rebuild",
            "max_retries": 1,
            "backoff_seconds": 1,
        },
        headers=auth_headers("fail-create"),
    ).json()["job"]

    first_failure = client.post(
        f"/v1/jobs/{created['id']}/fail",
        json={"error_message": "worker timeout"},
        headers=auth_headers("fail-1"),
    )
    second_failure = client.post(
        f"/v1/jobs/{created['id']}/fail",
        json={"error_message": "worker timeout again"},
        headers=auth_headers("fail-2"),
    )

    assert first_failure.status_code == 200
    assert first_failure.json()["state"] == "retry_pending"
    assert first_failure.json()["revision"] == 2
    assert first_failure.json()["next_run_at"] is not None
    assert second_failure.status_code == 200
    assert second_failure.json()["state"] == "failed"
    assert second_failure.json()["revision"] == 3


def test_list_and_stats_endpoints(client: TestClient) -> None:
    jobs = [
        {
            "job_type": "projection-build",
            "payload": {"projection": "orders"},
            "idempotency_key": "proj:orders:1",
            "priority": "critical",
        },
        {
            "job_type": "projection-build",
            "payload": {"projection": "inventory"},
            "idempotency_key": "proj:inventory:1",
            "priority": "low",
        },
    ]

    first = client.post("/v1/jobs", json=jobs[0], headers=auth_headers("stats-1")).json()["job"]
    client.post("/v1/jobs", json=jobs[1], headers=auth_headers("stats-2"))
    client.post(f"/v1/jobs/{first['id']}/dispatch", headers=auth_headers("stats-dispatch"))

    filtered = client.get("/v1/jobs", params={"priority": "critical"}, headers=auth_headers("filter"))
    stats = client.get("/v1/jobs/stats", headers=auth_headers("stats"))
    metrics = client.get("/metrics")

    assert filtered.status_code == 200
    assert filtered.json()["total"] == 1
    assert filtered.json()["items"][0]["priority"] == "critical"
    assert stats.status_code == 200
    assert stats.json()["total"] == 2
    assert stats.json()["running"] == 1
    assert metrics.status_code == 200
    assert "idempotent_orchestrator_http_requests_total" in metrics.text
