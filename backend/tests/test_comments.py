from fastapi.testclient import TestClient

from tests.conftest import auth_header, create_post, register


def _comment(client: TestClient, token: str, post_id: int, body: str = "A useful note.") -> dict:
    response = client.post(
        f"/api/v1/posts/{post_id}/comments",
        json={"body": body},
        headers=auth_header(token),
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_create_comment_requires_authentication(client: TestClient) -> None:
    token = register(client, "johndoe")["access_token"]
    post_id = create_post(client, token)["id"]
    response = client.post(f"/api/v1/posts/{post_id}/comments", json={"body": "Hello"})
    assert response.status_code == 401


def test_create_comment_on_missing_post_returns_404(client: TestClient) -> None:
    token = register(client, "johndoe")["access_token"]
    response = client.post(
        "/api/v1/posts/9999/comments",
        json={"body": "Hello"},
        headers=auth_header(token),
    )
    assert response.status_code == 404


def test_empty_comment_is_rejected(client: TestClient) -> None:
    token = register(client, "johndoe")["access_token"]
    post_id = create_post(client, token)["id"]
    response = client.post(
        f"/api/v1/posts/{post_id}/comments",
        json={"body": "   "},
        headers=auth_header(token),
    )
    assert response.status_code == 422


def test_other_users_and_anonymous_readers_can_list_comments(client: TestClient) -> None:
    author_token = register(client, "johndoe")["access_token"]
    reader_token = register(client, "janedoe")["access_token"]
    post_id = create_post(client, author_token)["id"]
    created = _comment(client, author_token, post_id, "First")
    _comment(client, reader_token, post_id, "Second")

    for headers in (None, auth_header(reader_token)):
        response = client.get(f"/api/v1/posts/{post_id}/comments", headers=headers)
        assert response.status_code == 200
        body = response.json()
        assert body["total"] == 2
        assert [item["body"] for item in body["items"]] == ["First", "Second"]
        assert body["items"][0]["id"] == created["id"]
        assert body["items"][0]["author"]["username"] == "johndoe"


def test_like_unlike_and_per_viewer_state(client: TestClient) -> None:
    author_token = register(client, "johndoe")["access_token"]
    reader_token = register(client, "janedoe")["access_token"]
    post_id = create_post(client, author_token)["id"]
    comment_id = _comment(client, author_token, post_id)["id"]
    like_url = f"/api/v1/posts/{post_id}/comments/{comment_id}/like"

    liked = client.post(like_url, headers=auth_header(reader_token))
    assert liked.status_code == 200
    assert liked.json() == {"liked": True, "like_count": 1}

    again = client.post(like_url, headers=auth_header(reader_token))
    assert again.status_code == 409

    listing = client.get(
        f"/api/v1/posts/{post_id}/comments",
        headers=auth_header(reader_token),
    ).json()["items"][0]
    assert listing["liked_by_current_user"] is True
    assert listing["like_count"] == 1

    author_view = client.get(
        f"/api/v1/posts/{post_id}/comments",
        headers=auth_header(author_token),
    ).json()["items"][0]
    assert author_view["liked_by_current_user"] is False
    assert author_view["like_count"] == 1

    anonymous = client.get(f"/api/v1/posts/{post_id}/comments").json()["items"][0]
    assert anonymous["liked_by_current_user"] is False

    unliked = client.delete(like_url, headers=auth_header(reader_token))
    assert unliked.status_code == 200
    assert unliked.json() == {"liked": False, "like_count": 0}


def test_author_can_update_and_delete_comment(client: TestClient) -> None:
    author_token = register(client, "johndoe")["access_token"]
    other_token = register(client, "janedoe")["access_token"]
    post_id = create_post(client, author_token)["id"]
    comment_id = _comment(client, author_token, post_id)["id"]
    url = f"/api/v1/posts/{post_id}/comments/{comment_id}"

    forbidden = client.put(url, json={"body": "Not yours"}, headers=auth_header(other_token))
    assert forbidden.status_code == 403
    forbidden_delete = client.delete(url, headers=auth_header(other_token))
    assert forbidden_delete.status_code == 403

    updated = client.put(url, json={"body": "Edited note"}, headers=auth_header(author_token))
    assert updated.status_code == 200
    assert updated.json()["body"] == "Edited note"

    deleted = client.delete(url, headers=auth_header(author_token))
    assert deleted.status_code == 204
    listing = client.get(f"/api/v1/posts/{post_id}/comments").json()
    assert listing["total"] == 0


def test_deleting_post_removes_comments(client: TestClient, db) -> None:
    from app.models.comment import Comment

    token = register(client, "johndoe")["access_token"]
    post_id = create_post(client, token)["id"]
    comment_id = _comment(client, token, post_id)["id"]

    response = client.delete(f"/api/v1/posts/{post_id}", headers=auth_header(token))
    assert response.status_code == 204
    db.expire_all()
    assert db.get(Comment, comment_id) is None


def test_liking_a_missing_comment_returns_404(client: TestClient) -> None:
    token = register(client, "johndoe")["access_token"]
    post_id = create_post(client, token)["id"]
    response = client.post(
        f"/api/v1/posts/{post_id}/comments/9999/like",
        headers=auth_header(token),
    )
    assert response.status_code == 404
