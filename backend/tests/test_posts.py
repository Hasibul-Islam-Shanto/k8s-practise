from fastapi.testclient import TestClient

from tests.conftest import POST_PAYLOAD, auth_header, create_post, register


def test_create_post(client: TestClient) -> None:
    token = register(client, "johndoe")["access_token"]
    post = create_post(client, token)
    assert post["title"] == POST_PAYLOAD["title"]
    assert post["slug"] == "building-rest-apis-with-fastapi"
    assert post["author"]["username"] == "johndoe"
    assert [t["name"] for t in post["tags"]] == ["FastAPI", "Python"]
    assert post["like_count"] == 0
    assert post["liked_by_current_user"] is False


def test_create_post_requires_authentication(client: TestClient) -> None:
    response = client.post("/api/v1/posts", json=POST_PAYLOAD)
    assert response.status_code == 401


def test_create_post_validates_input(client: TestClient) -> None:
    token = register(client, "johndoe")["access_token"]
    for field, value in [
        ("title", "abc"),
        ("excerpt", ""),
        ("content", "too short"),
        ("tags", []),
    ]:
        response = client.post(
            "/api/v1/posts",
            json={**POST_PAYLOAD, field: value},
            headers=auth_header(token),
        )
        assert response.status_code == 422, field


def test_duplicate_titles_get_distinct_slugs(client: TestClient) -> None:
    token = register(client, "johndoe")["access_token"]
    first = create_post(client, token)
    second = create_post(client, token)
    assert first["slug"] != second["slug"]
    assert second["slug"] == "building-rest-apis-with-fastapi-2"


def test_get_single_post(client: TestClient) -> None:
    token = register(client, "johndoe")["access_token"]
    post_id = create_post(client, token)["id"]
    response = client.get(f"/api/v1/posts/{post_id}")
    assert response.status_code == 200
    assert response.json()["id"] == post_id


def test_get_missing_post_returns_404(client: TestClient) -> None:
    assert client.get("/api/v1/posts/9999").status_code == 404


def test_list_posts_is_paginated_and_newest_first(client: TestClient) -> None:
    token = register(client, "johndoe")["access_token"]
    for index in range(5):
        create_post(client, token, title=f"Technology Article Number {index}")

    response = client.get("/api/v1/posts", params={"page": 1, "limit": 2})
    assert response.status_code == 200
    body = response.json()
    assert body == {
        "items": body["items"],
        "page": 1,
        "limit": 2,
        "total": 5,
        "total_pages": 3,
    }
    assert len(body["items"]) == 2
    assert body["items"][0]["title"] == "Technology Article Number 4"

    page_two = client.get("/api/v1/posts", params={"page": 2, "limit": 2}).json()
    assert page_two["items"][0]["title"] == "Technology Article Number 2"


def test_list_posts_search_matches_title_author_and_tag(client: TestClient) -> None:
    token = register(client, "johndoe", full_name="Grace Hopper")["access_token"]
    create_post(client, token, title="Understanding Docker Networking", tags=["Docker"])
    create_post(client, token, title="Vue 3 Composition API Explained", tags=["Vue"])

    by_title = client.get("/api/v1/posts", params={"search": "docker"}).json()
    assert by_title["total"] == 1

    by_tag = client.get("/api/v1/posts", params={"search": "Vue"}).json()
    assert by_tag["total"] == 1

    by_author = client.get("/api/v1/posts", params={"search": "grace"}).json()
    assert by_author["total"] == 2

    no_match = client.get("/api/v1/posts", params={"search": "Kubernetes"}).json()
    assert no_match["total"] == 0
    assert no_match["items"] == []


def test_list_posts_filters_by_tag(client: TestClient) -> None:
    token = register(client, "johndoe")["access_token"]
    create_post(client, token, title="Getting Started with Linux", tags=["Linux"])
    create_post(client, token, title="Introduction to Terraform State", tags=["DevOps"])

    body = client.get("/api/v1/posts", params={"tag": "linux"}).json()
    assert body["total"] == 1
    assert body["items"][0]["title"] == "Getting Started with Linux"


def test_update_own_post(client: TestClient) -> None:
    token = register(client, "johndoe")["access_token"]
    post_id = create_post(client, token)["id"]
    response = client.put(
        f"/api/v1/posts/{post_id}",
        json={**POST_PAYLOAD, "title": "Understanding JavaScript Closures", "tags": ["JavaScript"]},
        headers=auth_header(token),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "Understanding JavaScript Closures"
    assert body["slug"] == "understanding-javascript-closures"
    assert [t["name"] for t in body["tags"]] == ["JavaScript"]


def test_cannot_update_another_users_post(client: TestClient) -> None:
    owner_token = register(client, "johndoe")["access_token"]
    other_token = register(client, "janedoe")["access_token"]
    post_id = create_post(client, owner_token)["id"]

    response = client.put(
        f"/api/v1/posts/{post_id}",
        json={**POST_PAYLOAD, "title": "Hijacking Someone Elses Article"},
        headers=auth_header(other_token),
    )
    assert response.status_code == 403
    assert client.get(f"/api/v1/posts/{post_id}").json()["title"] == POST_PAYLOAD["title"]


def test_delete_own_post(client: TestClient) -> None:
    token = register(client, "johndoe")["access_token"]
    post_id = create_post(client, token)["id"]
    response = client.delete(f"/api/v1/posts/{post_id}", headers=auth_header(token))
    assert response.status_code == 204
    assert client.get(f"/api/v1/posts/{post_id}").status_code == 404


def test_cannot_delete_another_users_post(client: TestClient) -> None:
    owner_token = register(client, "johndoe")["access_token"]
    other_token = register(client, "janedoe")["access_token"]
    post_id = create_post(client, owner_token)["id"]

    response = client.delete(f"/api/v1/posts/{post_id}", headers=auth_header(other_token))
    assert response.status_code == 403
    assert client.get(f"/api/v1/posts/{post_id}").status_code == 200


def test_tags_are_reused_case_insensitively(client: TestClient, db) -> None:
    from app.models.tag import Tag

    token = register(client, "johndoe")["access_token"]
    create_post(client, token, title="First Article About Python", tags=["Python"])
    create_post(client, token, title="Second Article About Python", tags=["python"])
    assert db.query(Tag).filter_by(slug="python").count() == 1
