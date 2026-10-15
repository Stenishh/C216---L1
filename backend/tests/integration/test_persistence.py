from fastapi.testclient import TestClient
from sqlalchemy import text

from src.database.session import get_db
from src.main import app


def test_data_survives_new_client_and_database_connection(client, session_factory):
    task = client.post("/tasks", json={"title": "Persistente"}).json()
    session_factory.kw["bind"].dispose()
    with TestClient(app) as restarted_client:
        response = restarted_client.get(f"/tasks/{task['id']}")
        assert response.status_code == 200
        assert response.json() == task
    with session_factory() as session:
        assert (
            session.execute(text("SELECT title FROM tasks")).scalar_one()
            == "Persistente"
        )
    assert get_db in app.dependency_overrides
