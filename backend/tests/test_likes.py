import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError

from tests.conftest import auth_header, create_post, register


def test_like_post(client: TestClient) -> None:
    author_token = register(client, "johndoe")["access_token"]
    reader_token = register(client, "janedoe")["access_token"]
    post_id = create_post(client, author_token)["id"]

    response = client.post(f"/api/v1/posts/{post_id}/like", headers=auth_header(reader_token))
    assert response.status_code == 200
    assert response.json() == {"liked": True, "like_count": 1}


def test_like_requires_authentication(client: TestClient) -> None:
    token = register(client, "johndoe")["access_token"]
    post_id = create_post(client, token)["id"]
    assert client.post(f"/api/v1/posts/{post_id}/like").status_code == 401


def test_liking_twice_is_rejected(client: TestClient) -> None:
    author_token = register(client, "johndoe")["access_token"]
    reader_token = register(client, "janedoe")["access_token"]
    post_id = create_post(client, author_token)["id"]

    client.post(f"/api/v1/posts/{post_id}/like", headers=auth_header(reader_token))
    response = client.post(f"/api/v1/posts/{post_id}/like", headers=auth_header(reader_token))
    assert response.status_code == 409
    assert client.get(f"/api/v1/posts/{post_id}").json()["like_count"] == 1


def test_database_rejects_duplicate_likes(client: TestClient, db) -> None:
    """The uniqueness guarantee must come from the schema, not the endpoint."""
    from app.models.like import Like

    author_token = register(client, "johndoe")["access_token"]
    reader = register(client, "janedoe")["user"]
    post_id = create_post(client, author_token)["id"]

    db.add(Like(user_id=reader["id"], post_id=post_id))
    db.commit()
    db.add(Like(user_id=reader["id"], post_id=post_id))
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()


def test_unlike_post(client: TestClient) -> None:
    author_token = register(client, "johndoe")["access_token"]
    reader_token = register(client, "janedoe")["access_token"]
    post_id = create_post(client, author_token)["id"]

    client.post(f"/api/v1/posts/{post_id}/like", headers=auth_header(reader_token))
    response = client.delete(f"/api/v1/posts/{post_id}/like", headers=auth_header(reader_token))
    assert response.status_code == 200
    assert response.json() == {"liked": False, "like_count": 0}


def test_unliking_a_post_that_was_not_liked_returns_404(client: TestClient) -> None:
    author_token = register(client, "johndoe")["access_token"]
    reader_token = register(client, "janedoe")["access_token"]
    post_id = create_post(client, author_token)["id"]

    response = client.delete(f"/api/v1/posts/{post_id}/like", headers=auth_header(reader_token))
    assert response.status_code == 404


def test_like_state_is_per_viewer(client: TestClient) -> None:
    author_token = register(client, "johndoe")["access_token"]
    reader_token = register(client, "janedoe")["access_token"]
    post_id = create_post(client, author_token)["id"]
    client.post(f"/api/v1/posts/{post_id}/like", headers=auth_header(reader_token))

    for token, expected in [(reader_token, True), (author_token, False)]:
        body = client.get(f"/api/v1/posts/{post_id}", headers=auth_header(token)).json()
        assert body["liked_by_current_user"] is expected
        assert body["like_count"] == 1

    anonymous = client.get(f"/api/v1/posts/{post_id}").json()
    assert anonymous["liked_by_current_user"] is False
    assert anonymous["like_count"] == 1


def test_liking_a_missing_post_returns_404(client: TestClient) -> None:
    token = register(client, "johndoe")["access_token"]
    assert client.post("/api/v1/posts/9999/like", headers=auth_header(token)).status_code == 404
