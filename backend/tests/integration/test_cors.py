import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.mark.parametrize("method", ["GET", "POST", "PUT", "PATCH", "DELETE"])
def test_cors_allows_crud(method):
    with TestClient(app) as client:
        response = client.options(
            "/orders/",
            headers={
                "Origin": "http://127.0.0.1:5173",
                "Access-Control-Request-Method": method,
                "Access-Control-Request-Headers": "content-type",
            },
        )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://127.0.0.1:5173"


def test_cors_rejects_unknown_origin():
    with TestClient(app) as client:
        response = client.options(
            "/orders/",
            headers={
                "Origin": "https://unknown.example",
                "Access-Control-Request-Method": "DELETE",
            },
        )
    assert response.status_code == 400
    assert "access-control-allow-origin" not in response.headers
