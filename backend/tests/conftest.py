from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app

# Tests run against in-memory SQLite so they need no MySQL server. StaticPool
# keeps every connection pointed at the same in-memory database.
engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


@pytest.fixture
def db() -> Generator[Session, None, None]:
    Base.metadata.create_all(engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


@pytest.fixture
def client(db: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def register(client: TestClient, username: str, **overrides: object) -> dict:
    """Create a user and return its token plus profile."""
    payload = {
        "full_name": overrides.get("full_name", f"{username.title()} Example"),
        "username": username,
        "email": overrides.get("email", f"{username}@example.com"),
        "password": overrides.get("password", "password123"),
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


def auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


POST_PAYLOAD = {
    "title": "Building REST APIs with FastAPI",
    "excerpt": "FastAPI makes building Python APIs simple and fast.",
    "content": "FastAPI gives you automatic validation and documentation. " * 5,
    "tags": ["Python", "FastAPI"],
}


def create_post(client: TestClient, token: str, **overrides: object) -> dict:
    payload = {**POST_PAYLOAD, **overrides}
    response = client.post("/api/v1/posts", json=payload, headers=auth_header(token))
    assert response.status_code == 201, response.text
    return response.json()
