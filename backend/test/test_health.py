from fastapi.testclient import TestClient

from app.main import create_app


def test_health_returns_ok(monkeypatch):
    monkeypatch.setenv("APP_ENV", "test")
    client = TestClient(create_app())

    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["app_env"] == "test"


def test_health_does_not_expose_secrets(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "fake-key-for-test")
    client = TestClient(create_app())

    response = client.get("/health")

    assert "fake-key-for-test" not in response.text
