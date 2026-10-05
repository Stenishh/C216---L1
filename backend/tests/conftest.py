import pytest
from fastapi.testclient import TestClient

from src.dependencies import get_task_service
from src.main import app
from src.repositories.tasks import TaskRepository
from src.services.tasks import TaskService


@pytest.fixture
def client():
    service = TaskService(TaskRepository())
    app.dependency_overrides[get_task_service] = lambda: service
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
