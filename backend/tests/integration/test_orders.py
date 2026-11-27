import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.models import OrderEvent, ServiceOrder
from src.models.enums import EventAction, OrderStatus
from src.repositories.orders import OrderRepository

VALID = {
    "equipment_type": "notebook",
    "brand": "  Dell  ",
    "model": "Inspiron",
    "serial_number": "ABC",
    "reported_problem": "Não liga",
}


@pytest.fixture
def payload(client):
    customer = client.post("/customers/", json={"name": "Ana", "phone": "35999998888"})
    return {**VALID, "customer_id": customer.json()["id"]}


def test_crud_persistence_and_opening_event(client, database, payload):
    assert client.get("/orders/").json() == []
    response = client.post("/orders/", json=payload)
    assert response.status_code == 201
    order = response.json()
    path = f"/orders/{order['id']}"
    assert response.headers["location"] == path
    assert order["brand"] == "Dell"
    assert order["status"] == "received"
    assert order["budget_decision"] == "not_requested"
    assert order["diagnosis"] is order["budget_amount"] is None
    assert order["created_at"] and order["updated_at"]
    engine, _ = database
    engine.dispose()
    assert client.get(path).json() == order
    with Session(engine) as session:
        events = list(
            session.scalars(
                select(OrderEvent).where(OrderEvent.order_id == order["id"])
            )
        )
        assert len(events) == 1
        assert events[0].action == EventAction.OPEN
        assert events[0].previous_status is None
        assert events[0].resulting_status == OrderStatus.RECEIVED
        assert events[0].created_at
    patched = client.patch(path, json={"brand": "Lenovo", "serial_number": None})
    assert patched.status_code == 200
    assert patched.json()["serial_number"] is None
    assert patched.json()["model"] == payload["model"]
    other = client.post(
        "/customers/", json={"name": "Bia", "phone": "35999998888"}
    ).json()
    replaced = client.put(
        path, json={**payload, "customer_id": other["id"], "serial_number": None}
    )
    assert replaced.status_code == 200
    assert replaced.json()["customer_id"] == other["id"]
    assert replaced.json()["created_at"] == order["created_at"]
    with Session(engine) as session:
        assert session.get(ServiceOrder, order["id"]).customer_id == other["id"]
        assert len(list(session.scalars(select(OrderEvent)))) == 1
    deleted = client.delete(path)
    assert deleted.status_code == 204 and deleted.content == b""
    assert client.get(path).status_code == 404
    with Session(engine) as session:
        assert session.get(ServiceOrder, order["id"]) is None
        assert list(session.scalars(select(OrderEvent))) == []


def test_list_newest_first_and_pagination(client, payload):
    ids = [client.post("/orders/", json=payload).json()["id"] for _ in range(3)]
    assert [o["id"] for o in client.get("/orders/").json()] == ids[::-1]
    assert [o["id"] for o in client.get("/orders/?offset=1&limit=1").json()] == [ids[1]]


@pytest.mark.parametrize(
    "changes",
    [
        {"brand": " "},
        {"brand": "x" * 101},
        {"model": " "},
        {"model": "x" * 101},
        {"reported_problem": " "},
        {"reported_problem": "x" * 2001},
        {"serial_number": "x" * 101},
        {"equipment_type": "phone"},
        {"customer_id": 0},
        {"customer_id": True},
        {"status": "delivered"},
        {"budget_amount": 10},
        {"diagnosis": "teste"},
    ],
)
def test_invalid_creation_has_no_side_effects(client, database, payload, changes):
    assert client.post("/orders/", json={**payload, **changes}).status_code == 422
    assert client.get("/orders/").json() == []
    with Session(database[0]) as session:
        assert list(session.scalars(select(OrderEvent))) == []


def test_missing_customer_and_invalid_updates_preserve_data(client, payload):
    assert (
        client.post("/orders/", json={**payload, "customer_id": 999999}).status_code
        == 404
    )
    order = client.post("/orders/", json=payload).json()
    path = f"/orders/{order['id']}"
    for body in (
        {},
        {"brand": None},
        {"customer_id": None},
        {"model": " "},
        {"status": "received"},
        {"id": 8},
        {"budget_decision": "approved"},
    ):
        assert client.patch(path, json=body).status_code == 422
    assert client.put(path, json={"brand": "Dell"}).status_code == 422
    for method in ("put", "patch"):
        assert (
            client.request(
                method, path, json={**payload, "customer_id": 999999}
            ).status_code
            == 404
        )
    assert client.get(path).json() == order


@pytest.mark.parametrize("method", ["get", "put", "patch", "delete"])
def test_missing_order(client, payload, method):
    kwargs = {"json": payload} if method in ("put", "patch") else {}
    assert client.request(method, "/orders/999999", **kwargs).status_code == 404


@pytest.mark.parametrize(
    "status", [s for s in OrderStatus if s != OrderStatus.RECEIVED]
)
def test_orders_with_progress_cannot_be_edited_or_deleted(
    client, database, payload, status
):
    order = client.post("/orders/", json=payload).json()
    with Session(database[0]) as session:
        session.get(ServiceOrder, order["id"]).status = status
        session.commit()
    path = f"/orders/{order['id']}"
    before = client.get(path).json()
    assert client.patch(path, json={"brand": "Outra"}).status_code == 409
    assert client.put(path, json=payload).status_code == 409
    assert client.delete(path).status_code == 409
    assert client.get(path).json() == before


def test_received_order_with_extra_event_cannot_be_deleted(client, database, payload):
    order = client.post("/orders/", json=payload).json()
    with Session(database[0]) as session:
        session.add(
            OrderEvent(
                order_id=order["id"],
                action=EventAction.BEGIN_DIAGNOSIS,
                previous_status=OrderStatus.RECEIVED,
                resulting_status=OrderStatus.IN_DIAGNOSIS,
            )
        )
        session.commit()
    assert client.delete(f"/orders/{order['id']}").status_code == 409
    with Session(database[0]) as session:
        assert len(list(session.scalars(select(OrderEvent)))) == 2


@pytest.mark.parametrize("params", [{"limit": 0}, {"limit": 101}, {"offset": -1}])
def test_invalid_pagination(client, params):
    assert client.get("/orders/", params=params).status_code == 422


@pytest.mark.parametrize("order_id", ["0", "-1", "abc"])
def test_invalid_id(client, order_id):
    assert client.get(f"/orders/{order_id}").status_code == 422


def test_customer_fk_race_is_handled(client, payload, monkeypatch):
    monkeypatch.setattr(
        OrderRepository, "customer_exists", lambda self, customer_id: True
    )
    assert (
        client.post("/orders/", json={**payload, "customer_id": 999999}).status_code
        == 404
    )
    order = client.post("/orders/", json=payload).json()
    path = f"/orders/{order['id']}"
    assert client.patch(path, json={"customer_id": 999999}).status_code == 404
    assert client.get(path).json() == order


def test_opening_event_failure_rolls_back_order(client, database, payload, monkeypatch):
    original = OrderRepository.create

    def invalid_event(self, data):
        order = original(self, data)
        order.events[0].resulting_status = None
        self.session.flush()
        return order

    monkeypatch.setattr(OrderRepository, "create", invalid_event)
    with pytest.raises(IntegrityError):
        client.post("/orders/", json=payload)
    with Session(database[0]) as session:
        assert list(session.scalars(select(ServiceOrder))) == []
        assert list(session.scalars(select(OrderEvent))) == []
