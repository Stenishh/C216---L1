import pytest

from src.main import app, health, info


def test_health_identifica_servico():
    assert health()["service"] == "backend"


def test_health_indica_servico_ativo():
    assert health()["state"] == "up"


@pytest.mark.parametrize(
    ("campo", "esperado"),
    [
        ("disciplina", "C216 - Sistemas Distribuidos"),
        ("instituicao", "INATEL"),
        ("periodo", "2026.2"),
    ],
)
def test_info_retorna_dados_academicos(campo, esperado):
    assert info()[campo] == esperado


def test_info_reflete_versao_da_aplicacao(monkeypatch):
    monkeypatch.setattr(app, "version", "2.0.0")
    assert info()["versao"] == "2.0.0"


def test_info_retorna_dados_independentes_entre_chamadas():
    resultado = info()
    resultado["instituicao"] = "Outra instituicao"
    assert info()["instituicao"] == "INATEL"


@pytest.mark.parametrize(
    ("rota", "esperado"),
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
def test_rotas_retornam_json(client, rota, esperado):
    resposta = client.get(rota)
    assert resposta.status_code == 200
    assert resposta.headers["content-type"] == "application/json"
    assert resposta.json() == esperado


@pytest.mark.parametrize(
    ("metodo", "rota", "status", "detalhe"),
    [
        ("GET", "/inexistente", 404, "Not Found"),
        ("POST", "/health", 405, "Method Not Allowed"),
        ("POST", "/info", 405, "Method Not Allowed"),
    ],
)
def test_requisicoes_invalidas_retornam_erro(client, metodo, rota, status, detalhe):
    resposta = client.request(metodo, rota)
    assert resposta.status_code == status
    assert resposta.json() == {"detail": detalhe}
