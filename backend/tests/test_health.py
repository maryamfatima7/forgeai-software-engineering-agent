from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint_returns_expected_structure() -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "forgeai-api"
    assert body["version"] == "0.1.0"
    assert "timestamp" in body


def test_versioned_health_endpoint_is_available() -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
