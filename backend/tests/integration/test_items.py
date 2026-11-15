import pytest


def test_items_persist_and_reject_duplicate(client):
    assert client.get("/items/").json() == []
    data = {"name": "Notebook", "description": None}
    response = client.post("/items/", json=data)
    assert response.status_code == 201
    assert response.json() == {"id": response.json()["id"], **data}
    assert client.get("/items/").json() == [response.json()]
    duplicate = client.post("/items/", json=data)
    assert duplicate.status_code == 409
    assert "esse nome" in duplicate.json()["detail"]
    assert client.post("/items/", json={"name": "Mouse"}).status_code == 201


@pytest.mark.parametrize("name", ["", "   ", "a" * 101])
def test_invalid_name(client, name):
    assert client.post("/items/", json={"name": name}).status_code == 422


@pytest.mark.parametrize(
    "origin,allowed",
    [
        ("http://localhost:5173", True),
        ("http://127.0.0.1:5173", True),
        ("http://unknown.example", False),
    ],
)
def test_cors_preflight(client, origin, allowed):
    response = client.options(
        "/items/",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type",
        },
    )
    assert response.status_code == (200 if allowed else 400)
    assert response.headers.get("access-control-allow-origin") == (
        origin if allowed else None
    )
    assert "access-control-allow-credentials" not in response.headers


def test_cors_on_post(client):
    response = client.post(
        "/items/", json={"name": "CORS"}, headers={"Origin": "http://localhost:5173"}
    )
    assert response.status_code == 201
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
