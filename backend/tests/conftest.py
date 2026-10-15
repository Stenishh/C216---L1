import os

import pytest
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from alembic import command
from src.database.session import get_db
from src.main import app
from src.repositories.tasks import TaskRepository
from src.services.tasks import TaskService


@pytest.fixture
def session_factory(tmp_path, monkeypatch):
    # TEST_DATABASE_URL deve apontar exclusivamente para um banco de testes.
    url = os.getenv("TEST_DATABASE_URL", f"sqlite:///{tmp_path / 'test.db'}")
    monkeypatch.setattr("src.core.config.DATABASE_URL", url)
    config = Config("alembic.ini")
    command.upgrade(config, "head")
    engine = create_engine(url)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    yield factory
    engine.dispose()
    command.downgrade(config, "base")


@pytest.fixture
def service(session_factory):
    with session_factory() as session:
        yield TaskService(TaskRepository(session))


@pytest.fixture
def client(session_factory):
    def override_db():
        with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
