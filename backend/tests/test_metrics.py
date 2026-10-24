import logging

from fastapi.testclient import TestClient


def test_metrics_endpoint(client: TestClient) -> None:
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
    body = response.text
    assert "# HELP" in body
    assert "http_requests" in body


def test_health_returns_request_id(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.headers["x-request-id"]


def test_incoming_request_id_is_echoed(client: TestClient) -> None:
    response = client.get("/health", headers={"X-Request-ID": "trace-123"})
    assert response.headers["x-request-id"] == "trace-123"


def test_access_log_includes_request_id(client: TestClient, caplog) -> None:
    with caplog.at_level(logging.INFO, logger="app"):
        response = client.get("/health", headers={"X-Request-ID": "trace-abc"})

    matches = [
        record
        for record in caplog.records
        if getattr(record, "event", None) == "http_request"
        and getattr(record, "request_id", None) == "trace-abc"
    ]
    assert matches
    assert matches[-1].path == "/health"
    assert matches[-1].status_code == response.status_code
