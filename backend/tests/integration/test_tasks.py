import pytest


def test_task_lifecycle(client):
    assert client.get("/tasks").json() == []
    response = client.post("/tasks", json={"title": "  Pratica 4  "})
    assert response.status_code == 201
    task = response.json()
    assert task == {
        "id": 1,
        "title": "Pratica 4",
        "description": "",
        "completed": False,
    }
    assert response.headers["location"] == "/tasks/1"
    assert client.get("/tasks/1").json() == task
    response = client.put(
        "/tasks/1",
        json={
            "title": "Relatorio",
            "description": "Escrever decisoes",
            "completed": True,
        },
    )
    assert response.status_code == 200
    assert response.json()["completed"] is True
    response = client.patch("/tasks/1", json={"completed": False})
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "title": "Relatorio",
        "description": "Escrever decisoes",
        "completed": False,
    }
    response = client.delete("/tasks/1")
    assert response.status_code == 204
    assert response.content == b""
    assert client.get("/tasks/1").status_code == 404
    assert client.get("/tasks").json() == []


def test_filter_and_pagination(client):
    for index in range(4):
        client.post("/tasks", json={"title": str(index), "completed": index % 2 == 0})
    response = client.get("/tasks", params={"completed": True, "offset": 1, "limit": 1})
    assert response.status_code == 200
    assert [task["title"] for task in response.json()] == ["2"]
    assert len(client.get("/tasks", params={"completed": False}).json()) == 2
    assert client.get("/tasks", params={"offset": 10}).json() == []


@pytest.mark.parametrize("method", ["GET", "PUT", "PATCH", "DELETE"])
def test_missing_task(client, method):
    response = client.request(
        method,
        "/tasks/999",
        json={
            "title": "Tarefa",
            "description": "",
            "completed": False,
        },
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Tarefa nao encontrada"}


@pytest.mark.parametrize("task_id", ["0", "-1", "abc"])
@pytest.mark.parametrize("method", ["GET", "PUT", "PATCH", "DELETE"])
def test_invalid_path(client, task_id, method):
    assert (
        client.request(
            method,
            f"/tasks/{task_id}",
            json={
                "title": "Tarefa",
                "description": "",
                "completed": False,
            },
        ).status_code
        == 422
    )


@pytest.mark.parametrize(
    "params",
    [
        {"offset": -1},
        {"limit": 0},
        {"limit": 101},
        {"completed": "invalid"},
    ],
)
def test_invalid_query(client, params):
    assert client.get("/tasks", params=params).status_code == 422


@pytest.mark.parametrize(
    ("method", "payload"),
    [
        ("POST", {}),
        ("POST", {"title": "  "}),
        ("POST", {"title": "x" * 121}),
        ("POST", {"title": "Tarefa", "description": "x" * 1001}),
        ("POST", {"title": "Tarefa", "id": 9}),
        ("PUT", {"title": "Tarefa"}),
        ("PATCH", {}),
        ("PATCH", {"title": None}),
        ("PATCH", {"completed": None}),
        ("PATCH", {"description": None}),
        ("PATCH", {"title": " "}),
        ("PATCH", {"id": 9}),
    ],
)
def test_invalid_body_does_not_change_state(client, method, payload):
    original = client.post("/tasks", json={"title": "Original"}).json()
    route = "/tasks" if method == "POST" else "/tasks/1"
    assert client.request(method, route, json=payload).status_code == 422
    assert client.get("/tasks/1").json() == original
    assert len(client.get("/tasks").json()) == 1


def test_put_is_idempotent_and_patch_accepts_empty_description(client):
    client.post("/tasks", json={"title": "Original", "description": "Anterior"})
    payload = {"title": "Nova", "description": "Texto", "completed": True}
    assert (
        client.put("/tasks/1", json=payload).json()
        == client.put("/tasks/1", json=payload).json()
    )
    assert (
        client.patch("/tasks/1", json={"description": ""}).json()["description"] == ""
    )
