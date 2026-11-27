from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from threading import Barrier

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.models import OrderEvent
from src.repositories.orders import OrderRepository


def open_order(client):
    customer = client.post(
        "/customers/", json={"name": "Ana", "phone": "35999998888"}
    ).json()
    response = client.post(
        "/orders/",
        json={
            "customer_id": customer["id"],
            "equipment_type": "notebook",
            "brand": "Dell",
            "model": "Inspiron",
            "reported_problem": "Não liga",
        },
    )
    assert response.status_code == 201
    return response.headers["location"]


def advance(client, path, status):
    if status == "received":
        return
    if status == "cancelled":
        assert (
            client.post(f"{path}/cancel", json={"reason": "Desistência"}).status_code
            == 200
        )
        return
    assert client.post(f"{path}/begin-diagnosis").status_code == 200
    if status == "in_diagnosis":
        return
    assert (
        client.patch(
            f"{path}/diagnosis", json={"diagnosis": "Fonte", "budget_amount": "100.50"}
        ).status_code
        == 200
    )
    assert client.post(f"{path}/request-approval").status_code == 200
    if status == "awaiting_approval":
        return
    assert client.post(f"{path}/approve-budget").status_code == 200
    assert client.post(f"{path}/start-repair").status_code == 200
    if status == "in_repair":
        return
    assert (
        client.patch(
            f"{path}/repair", json={"service_performed": "Fonte substituída"}
        ).status_code
        == 200
    )
    assert client.post(f"{path}/complete-repair").status_code == 200
    if status == "completed":
        return
    assert client.post(f"{path}/deliver", json={"confirmed": True}).status_code == 200


@pytest.fixture
def path(client):
    return open_order(client)


def test_full_workflow_history_and_persistence(client, database, path):
    advance(client, path, "in_repair")
    before = client.get(f"{path}/history").json()
    assert client.post(f"{path}/complete-repair").status_code == 409
    assert (
        client.patch(
            f"{path}/repair", json={"service_performed": "  Fonte substituída  "}
        ).json()["service_performed"]
        == "Fonte substituída"
    )
    assert client.get(f"{path}/history").json() == before
    assert (
        client.patch(f"{path}/repair", json={"service_performed": None}).status_code
        == 200
    )
    assert client.post(f"{path}/complete-repair").status_code == 409
    client.patch(f"{path}/repair", json={"service_performed": "Fonte nova"})
    completed = client.post(f"{path}/complete-repair")
    assert completed.status_code == 200 and completed.json()["status"] == "completed"
    assert client.post(f"{path}/complete-repair").status_code == 409
    delivered = client.post(f"{path}/deliver", json={"confirmed": True})
    assert delivered.status_code == 200 and delivered.json()["status"] == "delivered"
    database[0].dispose()
    assert client.get(path).json() == delivered.json()
    history = client.get(f"{path}/history").json()
    assert [e["action"] for e in history] == [
        "open",
        "begin_diagnosis",
        "request_approval",
        "approve_budget",
        "start_repair",
        "complete_repair",
        "deliver",
    ]
    assert [e["resulting_status"] for e in history] == [
        "received",
        "in_diagnosis",
        "awaiting_approval",
        "awaiting_approval",
        "in_repair",
        "completed",
        "delivered",
    ]
    assert history[0]["previous_status"] is None
    assert [e["previous_status"] for e in history[1:]] == [
        e["resulting_status"] for e in history[:-1]
    ]
    assert history[3]["approved_amount"] == "100.50"
    assert all(
        datetime.fromisoformat(e["created_at"]).utcoffset().total_seconds() == 0
        for e in history
    )
    assert all(e["order_id"] == delivered.json()["id"] for e in history)


@pytest.mark.parametrize(
    "status", ["received", "in_diagnosis", "awaiting_approval", "approved"]
)
def test_cancel_before_repair_preserves_data_and_decision(
    client, database, path, status
):
    advance(client, path, "awaiting_approval" if status == "approved" else status)
    if status == "approved":
        client.post(f"{path}/approve-budget")
    before = client.get(path).json()
    response = client.post(f"{path}/cancel", json={"reason": "  Cliente desistiu  "})
    assert response.status_code == 200
    cancelled = response.json()
    assert cancelled["status"] == "cancelled"
    assert cancelled["cancellation_reason"] == "Cliente desistiu"
    assert cancelled["budget_decision"] == before["budget_decision"]
    assert cancelled["diagnosis"] == before["diagnosis"]
    assert cancelled["budget_amount"] == before["budget_amount"]
    database[0].dispose()
    assert client.get(path).json() == cancelled
    history = client.get(f"{path}/history").json()
    assert history[-1]["action"] == "cancel"
    assert history[-1]["observation"] == "Cliente desistiu"
    assert history[-1]["previous_status"] == before["status"]
    assert history[-1]["resulting_status"] == "cancelled"
    assert client.post(f"{path}/cancel", json={"reason": "Outra"}).status_code == 409
    assert client.delete(path).status_code == 409
    assert client.get(f"{path}/history").json() == history


@pytest.mark.parametrize(
    "status",
    [
        "received",
        "in_diagnosis",
        "awaiting_approval",
        "in_repair",
        "completed",
        "delivered",
        "cancelled",
    ],
)
def test_new_operations_reject_invalid_states_without_changes(client, path, status):
    advance(client, path, status)
    before = client.get(path).json()
    history = client.get(f"{path}/history").json()
    if status != "in_repair":
        assert (
            client.patch(
                f"{path}/repair", json={"service_performed": "Fonte"}
            ).status_code
            == 409
        )
        assert client.post(f"{path}/complete-repair").status_code == 409
    if status != "completed":
        assert (
            client.post(f"{path}/deliver", json={"confirmed": True}).status_code == 409
        )
    if status in ("in_repair", "completed", "delivered", "cancelled"):
        assert (
            client.post(f"{path}/cancel", json={"reason": "Custo"}).status_code == 409
        )
    assert client.get(path).json() == before
    assert client.get(f"{path}/history").json() == history


@pytest.mark.parametrize("status", ["completed", "delivered", "cancelled"])
def test_closed_order_data_cannot_be_changed(client, path, status):
    advance(client, path, status)
    before = client.get(path).json()
    history = client.get(f"{path}/history").json()
    assert client.patch(path, json={"brand": "Outra"}).status_code == 409
    assert (
        client.patch(f"{path}/diagnosis", json={"diagnosis": "Outro"}).status_code
        == 409
    )
    assert (
        client.patch(f"{path}/repair", json={"service_performed": "Outro"}).status_code
        == 409
    )
    for action in (
        "begin-diagnosis",
        "request-approval",
        "approve-budget",
        "start-repair",
        "complete-repair",
    ):
        assert client.post(f"{path}/{action}").status_code == 409
    assert (
        client.post(f"{path}/reject-budget", json={"reason": "Outro"}).status_code
        == 409
    )
    assert client.delete(path).status_code == 409
    assert client.get(path).json() == before
    assert client.get(f"{path}/history").json() == history


@pytest.mark.parametrize(
    "body",
    [
        {},
        {"service_performed": " "},
        {"service_performed": "x" * 2001},
        {"service_performed": "Fonte", "status": "completed"},
    ],
)
def test_invalid_repair_preserves_data(client, path, body):
    advance(client, path, "in_repair")
    before = client.get(path).json()
    assert client.patch(f"{path}/repair", json=body).status_code == 422
    assert client.get(path).json() == before


@pytest.mark.parametrize(
    "body",
    [
        None,
        {},
        {"confirmed": False},
        {"confirmed": "true"},
        {"confirmed": 1},
        {"confirmed": True, "status": "delivered"},
    ],
)
def test_delivery_requires_explicit_confirmation(client, path, body):
    advance(client, path, "completed")
    before = client.get(path).json()
    assert client.post(f"{path}/deliver", json=body).status_code == 422
    assert client.get(path).json() == before


@pytest.mark.parametrize(
    "body",
    [
        {},
        {"reason": " "},
        {"reason": None},
        {"reason": "x" * 501},
        {"reason": "Outro", "status": "cancelled"},
    ],
)
def test_invalid_cancellation_has_no_event(client, path, body):
    before = client.get(path).json()
    assert client.post(f"{path}/cancel", json=body).status_code == 422
    assert client.get(path).json() == before
    assert len(client.get(f"{path}/history").json()) == 1


def test_history_is_scoped_paginated_and_read_only(client, path):
    advance(client, path, "delivered")
    other = open_order(client)
    history = client.get(f"{path}/history").json()
    assert client.get(f"{path}/history?offset=2&limit=2").json() == history[2:4]
    assert client.get(f"{path}/history?offset=100").json() == []
    assert len(client.get(f"{other}/history").json()) == 1
    for query in ("offset=-1", "limit=0", "limit=101"):
        assert client.get(f"{path}/history?{query}").status_code == 422
    for method in ("post", "put", "patch", "delete"):
        assert client.request(method, f"{path}/history", json={}).status_code == 405
    assert client.get(f"{path}/history").json() == history


@pytest.mark.parametrize(
    "method,suffix,body",
    [
        ("patch", "repair", {"service_performed": "Fonte"}),
        ("post", "complete-repair", None),
        ("post", "deliver", {"confirmed": True}),
        ("post", "cancel", {"reason": "Custo"}),
        ("get", "history", None),
    ],
)
def test_missing_order_and_invalid_id(client, method, suffix, body):
    for order_id, status in (("999999", 404), ("0", 422), ("abc", 422)):
        assert (
            client.request(
                method,
                f"/orders/{order_id}/{suffix}",
                **({"json": body} if body is not None else {}),
            ).status_code
            == status
        )


@pytest.mark.parametrize(
    "action,stage,body",
    [
        ("complete-repair", "in_repair", None),
        ("deliver", "completed", {"confirmed": True}),
        ("cancel", "awaiting_approval", {"reason": "Custo"}),
    ],
)
def test_event_failure_rolls_back_new_transition(
    client, database, path, monkeypatch, action, stage, body
):
    advance(client, path, stage)
    if action == "complete-repair":
        client.patch(f"{path}/repair", json={"service_performed": "Fonte"})
    before = client.get(path).json()
    history = client.get(f"{path}/history").json()
    original = OrderRepository.add_event

    def invalid_event(self, order, event_action, previous_status, **kwargs):
        original(self, order, event_action, previous_status, **kwargs)
        self.session.add(
            OrderEvent(order_id=order.id, action=event_action, resulting_status=None)
        )
        self.session.flush()

    monkeypatch.setattr(OrderRepository, "add_event", invalid_event)
    with pytest.raises(IntegrityError):
        client.post(f"{path}/{action}", **({"json": body} if body is not None else {}))
    assert client.get(path).json() == before
    assert client.get(f"{path}/history").json() == history
    with Session(database[0]) as session:
        assert len(list(session.scalars(select(OrderEvent)))) == len(history)


def test_concurrent_repair_and_cancel_allow_only_one_transition(client, path):
    advance(client, path, "awaiting_approval")
    client.post(f"{path}/approve-budget")
    barrier = Barrier(2)

    def act(action):
        barrier.wait(timeout=10)
        return client.post(
            f"{path}/{action}",
            **({"json": {"reason": "Desistência"}} if action == "cancel" else {}),
        )

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(act, ("start-repair", "cancel")))
    assert sorted(r.status_code for r in results) == [200, 409]
    history = client.get(f"{path}/history").json()
    assert len(history) == 5
    assert history[-1]["resulting_status"] == client.get(path).json()["status"]
    assert history[-1]["action"] in ("start_repair", "cancel")
