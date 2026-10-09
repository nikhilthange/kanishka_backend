from fastapi.testclient import TestClient
from app.models.user import User


def test_register_user_success(client: TestClient):
    response = client.post(
        "/api/auth/register",
        json={
            "name": "New Person",
            "email": "newperson@example.com",
            "password": "SecurePassword123!",
            "role": "user",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New Person"
    assert data["email"] == "newperson@example.com"
    assert data["role"] == "user"
    assert "id" in data
    assert "password" not in data  # Never expose password in response


def test_register_duplicate_email_fails(client: TestClient, test_users: dict[str, User]):
    response = client.post(
        "/api/auth/register",
        json={
            "name": "Duplicate User",
            "email": "user1@test.com",  # already exists
            "password": "Password123!",
            "role": "user",
        },
    )
    assert response.status_code == 409
    assert "already registered" in response.json()["detail"].lower()


def test_register_invalid_data(client: TestClient):
    response = client.post(
        "/api/auth/register",
        json={
            "name": "",
            "email": "not-an-email",
            "password": "123",  # too short
        },
    )
    assert response.status_code == 422


def test_login_success(client: TestClient, test_users: dict[str, User]):
    response = client.post(
        "/api/auth/login",
        json={
            "email": "user1@test.com",
            "password": "UserOneSecret123!",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "user1@test.com"
    assert data["user"]["role"] == "user"


def test_login_invalid_password(client: TestClient, test_users: dict[str, User]):
    response = client.post(
        "/api/auth/login",
        json={
            "email": "user1@test.com",
            "password": "WrongPassword!",
        },
    )
    assert response.status_code == 401
    assert "invalid email or password" in response.json()["detail"].lower()


def test_login_nonexistent_email(client: TestClient):
    response = client.post(
        "/api/auth/login",
        json={
            "email": "ghost@test.com",
            "password": "SomePassword123!",
        },
    )
    assert response.status_code == 401


def test_get_me_authenticated(client: TestClient, auth_headers: dict[str, dict[str, str]]):
    response = client.get("/api/auth/me", headers=auth_headers["user1"])
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "user1@test.com"
    assert data["role"] == "user"


def test_get_me_unauthenticated(client: TestClient):
    response = client.get("/api/auth/me")
    assert response.status_code == 401
