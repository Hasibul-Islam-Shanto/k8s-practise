"""The complete user journey from requirement section 45, end to end."""

from fastapi.testclient import TestClient

from tests.conftest import POST_PAYLOAD, auth_header, create_post, register


def test_full_reader_and_author_journey(client: TestClient) -> None:
    # An existing author has already published something.
    author_token = register(client, "gracehopper", full_name="Grace Hopper")["access_token"]
    existing = create_post(
        client,
        author_token,
        title="Understanding Goroutines in Go",
        tags=["Go", "System Design"],
    )

    # A visitor can browse the feed and read an article without an account.
    feed = client.get("/api/v1/posts").json()
    assert feed["total"] == 1
    assert client.get(f"/api/v1/posts/{existing['id']}").status_code == 200

    # They register, which logs them straight in.
    session = register(client, "newreader", full_name="New Reader")
    token = session["access_token"]
    headers = auth_header(token)
    assert client.get("/api/v1/auth/me", headers=headers).json()["username"] == "newreader"

    # They like the article they just read.
    like = client.post(f"/api/v1/posts/{existing['id']}/like", headers=headers).json()
    assert like == {"liked": True, "like_count": 1}
    assert client.get(f"/api/v1/posts/{existing['id']}", headers=headers).json()[
        "liked_by_current_user"
    ]

    # They write their own article.
    own = create_post(
        client,
        token,
        title="What I Learned About Docker Networking",
        excerpt="Bridge and overlay networks, explained through my own mistakes.",
        tags=["Docker", "DevOps"],
    )

    # It appears on their profile, with the statistics updated.
    profile = client.get("/api/v1/users/newreader").json()
    assert profile["post_count"] == 1
    assert profile["total_likes_received"] == 0
    own_posts = client.get("/api/v1/users/newreader/posts").json()
    assert [item["id"] for item in own_posts["items"]] == [own["id"]]

    # They visit the other author's profile and browse their articles.
    other = client.get("/api/v1/users/gracehopper").json()
    assert other["post_count"] == 1
    assert other["total_likes_received"] == 1
    other_posts = client.get("/api/v1/users/gracehopper/posts").json()
    assert [item["id"] for item in other_posts["items"]] == [existing["id"]]

    # Search finds both articles by tag and by author.
    assert client.get("/api/v1/posts", params={"tag": "docker"}).json()["total"] == 1
    assert client.get("/api/v1/posts", params={"search": "grace"}).json()["total"] == 1

    # They can edit and then delete their own article, but not the other one.
    assert (
        client.put(
            f"/api/v1/posts/{existing['id']}",
            json={**POST_PAYLOAD, "title": "Trying To Edit Someone Elses Post"},
            headers=headers,
        ).status_code
        == 403
    )
    assert (
        client.put(
            f"/api/v1/posts/{own['id']}",
            json={
                "title": "What I Learned About Docker Networking",
                "excerpt": "Bridge and overlay networks, with the corrections I owe you.",
                "content": own["content"],
                "tags": ["Docker"],
            },
            headers=headers,
        ).status_code
        == 200
    )

    # Unliking returns the count to zero.
    assert client.delete(f"/api/v1/posts/{existing['id']}/like", headers=headers).json() == {
        "liked": False,
        "like_count": 0,
    }

    # Updating their profile is reflected publicly.
    client.put(
        "/api/v1/users/me",
        json={"full_name": "New Reader", "bio": "Learning in public."},
        headers=headers,
    )
    assert client.get("/api/v1/users/newreader").json()["bio"] == "Learning in public."

    assert client.delete(f"/api/v1/posts/{own['id']}", headers=headers).status_code == 204
    assert client.get("/api/v1/users/newreader").json()["post_count"] == 0
