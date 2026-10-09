from fastapi.testclient import TestClient
from app.models.task import Task


def test_ai_generate_description_authenticated(
    client: TestClient,
    auth_headers: dict[str, dict[str, str]],
):
    payload = {"title": "Deploy Redis Cluster with Sentinel"}
    response = client.post(
        "/api/tasks/generate-description",
        json=payload,
        headers=auth_headers["user1"],
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == payload["title"]
    assert "description" in data
    assert len(data["description"]) > 20
    assert "provider" in data


def test_ai_generate_description_unauthenticated(client: TestClient):
    payload = {"title": "Test Title"}
    response = client.post("/api/tasks/generate-description", json=payload)
    assert response.status_code == 401


def test_ai_generate_description_validation_error(
    client: TestClient,
    auth_headers: dict[str, dict[str, str]],
):
    # Empty title
    payload = {"title": ""}
    response = client.post(
        "/api/tasks/generate-description",
        json=payload,
        headers=auth_headers["user1"],
    )
    assert response.status_code == 422


def test_ai_generate_description_with_provider_override(
    client: TestClient,
    auth_headers: dict[str, dict[str, str]],
):
    payload = {"title": "Build WebSocket Real-Time Chat", "provider": "anthropic"}
    response = client.post(
        "/api/tasks/generate-description",
        json=payload,
        headers=auth_headers["user1"],
    )
    assert response.status_code == 200
    data = response.json()
    assert "description" in data
    assert "provider" in data


def test_ai_summarize_own_task(
    client: TestClient,
    auth_headers: dict[str, dict[str, str]],
    sample_tasks: list[Task],
):
    target_task = sample_tasks[0]  # user1's task
    response = client.post(
        f"/api/tasks/{target_task.id}/summarize",
        headers=auth_headers["user1"],
    )
    assert response.status_code == 200
    data = response.json()
    assert data["task_id"] == target_task.id
    assert "summary" in data
    assert len(data["summary"]) > 10


def test_ai_summarize_another_users_task_forbidden(
    client: TestClient,
    auth_headers: dict[str, dict[str, str]],
    sample_tasks: list[Task],
):
    # sample_tasks[2] belongs to user2. User1 tries to summarize it.
    target_task = sample_tasks[2]
    response = client.post(
        f"/api/tasks/{target_task.id}/summarize",
        headers=auth_headers["user1"],
    )
    assert response.status_code == 403
    assert "access denied" in response.json()["detail"].lower()


def test_ai_summarize_admin_can_summarize_any_task(
    client: TestClient,
    auth_headers: dict[str, dict[str, str]],
    sample_tasks: list[Task],
):
    target_task = sample_tasks[2]  # user2's task
    response = client.post(
        f"/api/tasks/{target_task.id}/summarize",
        headers=auth_headers["admin"],
    )
    assert response.status_code == 200
    data = response.json()
    assert data["task_id"] == target_task.id
    assert "summary" in data


def test_ai_summarize_nonexistent_task(
    client: TestClient,
    auth_headers: dict[str, dict[str, str]],
):
    response = client.post("/api/tasks/99999/summarize", headers=auth_headers["user1"])
    assert response.status_code == 404
