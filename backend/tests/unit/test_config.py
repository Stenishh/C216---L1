import pytest

from src.core.config import get_database_url


def test_database_url_is_required(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with pytest.raises(RuntimeError, match="Configure DATABASE_URL"):
        get_database_url()


@pytest.mark.parametrize(
    "value",
    [
        "invalid",
        "sqlite:///test.db",
        "postgresql+psycopg://localhost",
    ],
)
def test_database_url_rejects_wrong_driver_or_missing_database(monkeypatch, value):
    monkeypatch.setenv("DATABASE_URL", value)
    with pytest.raises(ValueError, match="PostgreSQL"):
        get_database_url()


def test_database_url_uses_environment_without_exposing_password(monkeypatch):
    value = "postgresql+psycopg://user:example@localhost/repara"
    monkeypatch.setenv("DATABASE_URL", value)
    assert get_database_url() == value
