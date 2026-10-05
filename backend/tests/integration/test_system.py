import pytest


@pytest.mark.parametrize(
    ("route", "expected"),
    [
        ("/health", {"service": "backend", "state": "up"}),
        (
            "/info",
            {
                "disciplina": "C216 - Sistemas Distribuidos",
                "instituicao": "INATEL",
                "periodo": "2026.2",
                "versao": "0.1.0",
            },
        ),
    ],
)
def test_system(client, route, expected):
    response = client.get(route)
    assert response.status_code == 200
    assert response.json() == expected


@pytest.mark.parametrize(
    ("method", "route", "code"),
    [
        ("GET", "/inexistente", 404),
        ("POST", "/health", 405),
        ("POST", "/info", 405),
    ],
)
def test_invalid_routes(client, method, route, code):
    assert client.request(method, route).status_code == code
