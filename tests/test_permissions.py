from fastapi.testclient import TestClient
from app.models.task import Task


def test_regular_user_cannot_view_another_users_task(
    client: TestClient,
    auth_headers: dict[str, dict[str, str]],
    sample_tasks: list[Task],
):
    # sample_tasks[2] belongs to user2. User1 tries to view it.
    target_task = sample_tasks[2]
    response = client.get(f"/api/tasks/{target_task.id}", headers=auth_headers["user1"])
    assert response.status_code == 403
    assert "access denied" in response.json()["detail"].lower()


def test_regular_user_cannot_edit_another_users_task(
    client: TestClient,
    auth_headers: dict[str, dict[str, str]],
    sample_tasks: list[Task],
):
    # sample_tasks[2] belongs to user2. User1 tries to edit it.
    target_task = sample_tasks[2]
    response = client.put(
        f"/api/tasks/{target_task.id}",
        json={"title": "Hacked Title"},
        headers=auth_headers["user1"],
    )
    assert response.status_code == 403
    assert "access denied" in response.json()["detail"].lower()


def test_regular_user_cannot_update_task_status_patch(
    client: TestClient,
    auth_headers: dict[str, dict[str, str]],
    sample_tasks: list[Task],
):
    # sample_tasks[0] belongs to user1. Even for their own task, user1 CANNOT update status!
    target_task = sample_tasks[0]
    response = client.patch(
        f"/api/tasks/{target_task.id}/status",
        json={"status": "Completed"},
        headers=auth_headers["user1"],
    )
    assert response.status_code == 403
    assert "regular users are not authorized to update task status" in response.json()["detail"].lower()


def test_regular_user_cannot_update_task_status_put(
    client: TestClient,
    auth_headers: dict[str, dict[str, str]],
    sample_tasks: list[Task],
):
    target_task = sample_tasks[0]
    response = client.put(
        f"/api/tasks/{target_task.id}/status",
        json={"status": "Completed"},
        headers=auth_headers["user1"],
    )
    assert response.status_code == 403


def test_admin_can_update_task_status(
    client: TestClient,
    auth_headers: dict[str, dict[str, str]],
    sample_tasks: list[Task],
):
    # Admin can update status of any task
    target_task = sample_tasks[0]
    response = client.patch(
        f"/api/tasks/{target_task.id}/status",
        json={"status": "Completed"},
        headers=auth_headers["admin"],
    )
    assert response.status_code == 200
    assert response.json()["status"] == "Completed"


def test_admin_can_edit_any_task(
    client: TestClient,
    auth_headers: dict[str, dict[str, str]],
    sample_tasks: list[Task],
):
    target_task = sample_tasks[0]
    response = client.put(
        f"/api/tasks/{target_task.id}",
        json={"title": "Admin Modified This Title"},
        headers=auth_headers["admin"],
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Admin Modified This Title"


def test_invalid_status_value_rejected(
    client: TestClient,
    auth_headers: dict[str, dict[str, str]],
    sample_tasks: list[Task],
):
    target_task = sample_tasks[0]
    response = client.patch(
        f"/api/tasks/{target_task.id}/status",
        json={"status": "NonExistentStatus"},
        headers=auth_headers["admin"],
    )
    assert response.status_code == 422


def test_unauthenticated_request_rejected(client: TestClient):
    response = client.get("/api/tasks/")
    assert response.status_code == 401
