from fastapi.testclient import TestClient

from tests.conftest import auth_header, create_post, register


def test_get_user_profile(client: TestClient) -> None:
    register(client, "johndoe", full_name="John Doe")
    response = client.get("/api/v1/users/johndoe")
    assert response.status_code == 200
    body = response.json()
    assert body["full_name"] == "John Doe"
    assert body["username"] == "johndoe"
    assert body["post_count"] == 0
    assert body["total_likes_received"] == 0
    # A public profile must not leak private fields.
    assert "email" not in body
    assert "password_hash" not in body


def test_get_missing_profile_returns_404(client: TestClient) -> None:
    assert client.get("/api/v1/users/nobody").status_code == 404


def test_profile_statistics_count_posts_and_likes_received(client: TestClient) -> None:
    author_token = register(client, "johndoe")["access_token"]
    reader_token = register(client, "janedoe")["access_token"]
    first = create_post(client, author_token, title="Understanding Goroutines in Go")
    create_post(client, author_token, title="How Nginx Reverse Proxy Works")
    client.post(f"/api/v1/posts/{first['id']}/like", headers=auth_header(reader_token))

    body = client.get("/api/v1/users/johndoe").json()
    assert body["post_count"] == 2
    assert body["total_likes_received"] == 1


def test_get_posts_by_username(client: TestClient) -> None:
    author_token = register(client, "johndoe")["access_token"]
    other_token = register(client, "janedoe")["access_token"]
    create_post(client, author_token, title="Understanding PostgreSQL Transactions")
    create_post(client, other_token, title="Introduction to Terraform State")

    body = client.get("/api/v1/users/johndoe/posts").json()
    assert body["total"] == 1
    assert body["items"][0]["title"] == "Understanding PostgreSQL Transactions"


def test_get_posts_for_user_without_posts(client: TestClient) -> None:
    register(client, "johndoe")
    body = client.get("/api/v1/users/johndoe/posts").json()
    assert body["total"] == 0
    assert body["items"] == []


def test_update_own_profile(client: TestClient) -> None:
    token = register(client, "johndoe")["access_token"]
    response = client.put(
        "/api/v1/users/me",
        json={
            "full_name": "Johnathan Doe",
            "bio": "Backend engineer interested in Python and APIs.",
            "avatar_url": "https://example.com/avatar.png",
        },
        headers=auth_header(token),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["full_name"] == "Johnathan Doe"
    assert body["bio"] == "Backend engineer interested in Python and APIs."
    assert body["avatar_url"] == "https://example.com/avatar.png"


def test_update_profile_requires_authentication(client: TestClient) -> None:
    response = client.put("/api/v1/users/me", json={"full_name": "Nobody At All"})
    assert response.status_code == 401


def test_update_profile_rejects_an_invalid_avatar_url(client: TestClient) -> None:
    token = register(client, "johndoe")["access_token"]
    response = client.put(
        "/api/v1/users/me",
        json={"avatar_url": "not a url"},
        headers=auth_header(token),
    )
    assert response.status_code == 422


def test_updating_a_profile_only_ever_affects_the_caller(client: TestClient) -> None:
    """There is no endpoint that accepts another user's identity, so the only
    way to write a profile is as that user."""
    register(client, "johndoe", full_name="John Doe")
    other_token = register(client, "janedoe")["access_token"]

    client.put(
        "/api/v1/users/me",
        json={"full_name": "Renamed By Jane"},
        headers=auth_header(other_token),
    )
    assert client.get("/api/v1/users/johndoe").json()["full_name"] == "John Doe"
    assert client.get("/api/v1/users/janedoe").json()["full_name"] == "Renamed By Jane"


def test_clearing_the_bio_stores_null(client: TestClient) -> None:
    token = register(client, "johndoe")["access_token"]
    client.put("/api/v1/users/me", json={"bio": "temporary"}, headers=auth_header(token))
    response = client.put("/api/v1/users/me", json={"bio": "  "}, headers=auth_header(token))
    assert response.json()["bio"] is None
