from fastapi.testclient import TestClient
from app.models.task import Task
from app.models.user import User


def test_create_task(client: TestClient, auth_headers: dict[str, dict[str, str]], test_users: dict[str, User]):
    payload = {
        "title": "Write Unit Tests",
        "description": "Ensure 100% test coverage for assessment submission.",
    }
    response = client.post("/api/tasks/", json=payload, headers=auth_headers["user1"])
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == payload["title"]
    assert data["description"] == payload["description"]
    assert data["status"] == "Pending"
    assert data["user_id"] == test_users["user1"].id


def test_list_tasks_regular_user_only_sees_own(
    client: TestClient,
    auth_headers: dict[str, dict[str, str]],
    sample_tasks: list[Task],
    test_users: dict[str, User],
):
    response = client.get("/api/tasks/", headers=auth_headers["user1"])
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    for task in data["tasks"]:
        assert task["user_id"] == test_users["user1"].id


def test_list_tasks_admin_sees_all(
    client: TestClient,
    auth_headers: dict[str, dict[str, str]],
    sample_tasks: list[Task],
):
    response = client.get("/api/tasks/", headers=auth_headers["admin"])
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 3


def test_get_own_task_success(
    client: TestClient,
    auth_headers: dict[str, dict[str, str]],
    sample_tasks: list[Task],
):
    target_task = sample_tasks[0]  # belongs to user1
    response = client.get(f"/api/tasks/{target_task.id}", headers=auth_headers["user1"])
    assert response.status_code == 200
    assert response.json()["id"] == target_task.id


def test_get_task_not_found(
    client: TestClient,
    auth_headers: dict[str, dict[str, str]],
):
    response = client.get("/api/tasks/99999", headers=auth_headers["user1"])
    assert response.status_code == 404


def test_edit_own_task(
    client: TestClient,
    auth_headers: dict[str, dict[str, str]],
    sample_tasks: list[Task],
):
    target_task = sample_tasks[0]  # user1's task
    update_data = {
        "title": "Updated Title for Task 1",
        "description": "Updated Description text",
    }
    response = client.put(f"/api/tasks/{target_task.id}", json=update_data, headers=auth_headers["user1"])
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == update_data["title"]
    assert data["description"] == update_data["description"]


def test_api_v1_alias_routing(
    client: TestClient,
    auth_headers: dict[str, dict[str, str]],
):
    response = client.get("/api/v1/tasks", headers=auth_headers["user1"])
    assert response.status_code == 200
    assert "tasks" in response.json()


def test_endpoint_without_trailing_slash(
    client: TestClient,
    auth_headers: dict[str, dict[str, str]],
):
    response = client.get("/api/tasks", headers=auth_headers["user1"])
    assert response.status_code == 200
    assert "tasks" in response.json()
