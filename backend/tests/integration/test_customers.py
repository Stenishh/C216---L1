import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models import Customer, OrderEvent, ServiceOrder
from src.models.enums import EquipmentType, EventAction, OrderStatus
from src.repositories.customers import CustomerRepository

VALID = {"name": "Ana Silva", "phone": "(35) 99999-8888", "email": "ana@example.com"}


def test_customer_crud_and_persistence(client, database):
    assert client.get("/customers/").json() == []
    response = client.post("/customers/", json=VALID)
    assert response.status_code == 201
    created = response.json()
    customer_id = created["id"]
    path = f"/customers/{customer_id}"
    assert response.headers["location"] == path
    assert created["phone"] == "35999998888"
    assert created["created_at"]
    engine, _ = database
    engine.dispose()
    assert client.get(path).json() == created
    with Session(engine) as session:
        assert session.get(Customer, customer_id).email == "ana@example.com"
    patched = client.patch(path, json={"name": "Ana Souza"})
    assert patched.status_code == 200
    assert patched.json()["phone"] == created["phone"]
    assert patched.json()["email"] == created["email"]
    assert client.patch(path, json={"email": None}).json()["email"] is None
    replaced = client.put(path, json={"name": "Ana", "phone": "3534721234"})
    assert replaced.status_code == 200
    assert replaced.json()["email"] is None
    assert replaced.json()["phone"] == "3534721234"
    assert replaced.json()["id"] == customer_id
    assert replaced.json()["created_at"] == created["created_at"]
    deleted = client.delete(path)
    assert deleted.status_code == 204
    assert deleted.content == b""
    assert client.get(path).status_code == 404
    assert client.get("/customers/").json() == []


def test_search_pagination_and_literal_wildcards(client):
    for name in ("Ana", "Bruno", "Ana 100%"):
        assert (
            client.post("/customers/", json={**VALID, "name": name}).status_code == 201
        )

    def names(response):
        return [item["name"] for item in response.json()]

    assert names(client.get("/customers/", params={"q": "ANA"})) == ["Ana", "Ana 100%"]
    assert names(client.get("/customers/", params={"q": "%"})) == ["Ana 100%"]
    assert names(client.get("/customers/", params={"q": "  Bruno  "})) == ["Bruno"]
    assert names(client.get("/customers/", params={"offset": 1, "limit": 1})) == [
        "Bruno"
    ]
    assert client.get("/customers/", params={"q": "inexistente"}).json() == []


def test_shared_contacts_are_allowed(client):
    first = client.post("/customers/", json=VALID)
    second = client.post("/customers/", json=VALID)
    assert first.status_code == second.status_code == 201
    assert first.json()["id"] != second.json()["id"]


@pytest.mark.parametrize("method", ["get", "put", "patch", "delete"])
def test_missing_customer_returns_404(client, method):
    response = client.request(
        method,
        "/customers/999999",
        **({"json": VALID} if method in ("put", "patch") else {}),
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Cliente não encontrado."}


@pytest.mark.parametrize(
    "body",
    [
        {"name": "Ana", "phone": "123"},
        {**VALID, "email": "invalido"},
        {"phone": "35999998888"},
    ],
)
def test_invalid_input_does_not_create_customer(client, body):
    assert client.post("/customers/", json=body).status_code == 422
    assert client.get("/customers/").json() == []


def test_invalid_update_preserves_existing_data(client):
    customer = client.post("/customers/", json=VALID).json()
    path = f"/customers/{customer['id']}"
    for body in ({}, {"name": None}, {"phone": "abc"}, {"id": 22}):
        assert client.patch(path, json=body).status_code == 422
    assert client.put(path, json={"name": "Ana"}).status_code == 422
    assert client.get(path).json() == customer


@pytest.mark.parametrize("params", [{"limit": 0}, {"limit": 101}, {"offset": -1}])
def test_invalid_pagination(client, params):
    assert client.get("/customers/", params=params).status_code == 422


@pytest.mark.parametrize("customer_id", ["0", "-1", "abc"])
def test_invalid_customer_id(client, customer_id):
    assert client.get(f"/customers/{customer_id}").status_code == 422


def link_order(engine, customer_id, status):
    with Session(engine) as session:
        order = ServiceOrder(
            customer_id=customer_id,
            equipment_type=EquipmentType.NOTEBOOK,
            brand="Marca",
            model="Modelo",
            reported_problem="Nao liga",
            status=status,
        )
        order.events.append(
            OrderEvent(action=EventAction.OPEN, resulting_status=OrderStatus.RECEIVED)
        )
        session.add(order)
        session.commit()
        return order.id


@pytest.mark.parametrize(
    "status", [OrderStatus.RECEIVED, OrderStatus.CANCELLED, OrderStatus.DELIVERED]
)
def test_linked_customer_cannot_be_deleted_in_any_order_status(
    client, database, status
):
    customer_id = client.post("/customers/", json=VALID).json()["id"]
    engine, _ = database
    order_id = link_order(engine, customer_id, status)
    response = client.delete(f"/customers/{customer_id}")
    assert response.status_code == 409
    assert response.json() == {
        "detail": "Não é possível excluir um cliente com ordens vinculadas."
    }
    with Session(engine) as session:
        assert session.get(Customer, customer_id) is not None
        assert session.get(ServiceOrder, order_id).status == status
        assert session.scalar(
            select(OrderEvent.id).where(OrderEvent.order_id == order_id)
        )


def test_foreign_key_conflict_is_handled_and_connection_recovers(
    client, database, monkeypatch
):
    customer_id = client.post("/customers/", json=VALID).json()["id"]
    engine, _ = database
    link_order(engine, customer_id, OrderStatus.RECEIVED)
    # Simula preconsulta desatualizada: a FK ainda deve proteger o cliente.
    monkeypatch.setattr(
        CustomerRepository, "has_orders", lambda self, customer_id: False
    )
    response = client.delete(f"/customers/{customer_id}")
    assert response.status_code == 409
    assert client.get(f"/customers/{customer_id}").status_code == 200
    assert (
        client.post("/customers/", json={**VALID, "name": "Bruno"}).status_code == 201
    )
