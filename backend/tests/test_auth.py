from fastapi.testclient import TestClient

from tests.conftest import auth_header, register


def test_register_user(client: TestClient) -> None:
    body = register(client, "johndoe")
    assert body["access_token"]
    assert body["user"]["username"] == "johndoe"
    assert body["user"]["email"] == "johndoe@example.com"
    assert "password" not in body["user"]
    assert "password_hash" not in body["user"]


def test_register_rejects_duplicate_email(client: TestClient) -> None:
    register(client, "johndoe")
    response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Another Person",
            "username": "another",
            "email": "johndoe@example.com",
            "password": "password123",
        },
    )
    assert response.status_code == 409


def test_register_rejects_duplicate_username(client: TestClient) -> None:
    register(client, "johndoe")
    response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Another Person",
            "username": "johndoe",
            "email": "other@example.com",
            "password": "password123",
        },
    )
    assert response.status_code == 409


def test_register_rejects_mismatched_confirmation(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "John Doe",
            "username": "johndoe",
            "email": "johndoe@example.com",
            "password": "password123",
            "confirm_password": "different123",
        },
    )
    assert response.status_code == 422


def test_register_rejects_short_password(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "John Doe",
            "username": "johndoe",
            "email": "johndoe@example.com",
            "password": "short",
        },
    )
    assert response.status_code == 422


def test_register_rejects_invalid_email(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "John Doe",
            "username": "johndoe",
            "email": "not-an-email",
            "password": "password123",
        },
    )
    assert response.status_code == 422


def test_login_with_email_and_with_username(client: TestClient) -> None:
    register(client, "johndoe")
    for identifier in ("johndoe@example.com", "johndoe"):
        response = client.post(
            "/api/v1/auth/login",
            json={"identifier": identifier, "password": "password123"},
        )
        assert response.status_code == 200, identifier
        assert response.json()["access_token"]


def test_login_with_wrong_password_is_rejected(client: TestClient) -> None:
    register(client, "johndoe")
    response = client.post(
        "/api/v1/auth/login",
        json={"identifier": "johndoe", "password": "wrongpassword"},
    )
    assert response.status_code == 401


def test_login_with_unknown_user_is_rejected(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={"identifier": "nobody", "password": "password123"},
    )
    assert response.status_code == 401


def test_me_returns_current_user(client: TestClient) -> None:
    token = register(client, "johndoe")["access_token"]
    response = client.get("/api/v1/auth/me", headers=auth_header(token))
    assert response.status_code == 200
    assert response.json()["username"] == "johndoe"


def test_me_requires_authentication(client: TestClient) -> None:
    assert client.get("/api/v1/auth/me").status_code == 401


def test_me_rejects_a_malformed_token(client: TestClient) -> None:
    response = client.get("/api/v1/auth/me", headers=auth_header("not-a-real-token"))
    assert response.status_code == 401


def test_password_is_hashed_in_the_database(client: TestClient, db) -> None:
    from app.models.user import User

    register(client, "johndoe")
    user = db.query(User).filter_by(username="johndoe").one()
    assert user.password_hash != "password123"
    assert user.password_hash.startswith("$2b$")
