"""Health endpoint tests."""


def test_health_reports_service_without_credentials(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "Indra-AI", "version": "0.1.0"}


def test_docs_are_available_in_development(client):
    response = client.get("/docs")

    assert response.status_code == 200


def test_request_id_is_returned_and_oversized_body_is_rejected(client):
    response = client.get("/health", headers={"X-Request-ID": "test-request-id"})
    assert response.headers["X-Request-ID"] == "test-request-id"

    oversized = client.post("/health", content=b"x" * (1_048_577))
    assert oversized.status_code == 413
    assert oversized.json()["error"]["code"] == "request_too_large"
