from fastapi.testclient import TestClient

from src.main import app


def test_health_reports_api_is_running():
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert response.json() == {"status": "ok", "service": "repara"}
