from decimal import Decimal

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.models import OrderEvent, ServiceOrder
from src.models.enums import BudgetDecision, EventAction, OrderStatus
from src.repositories.orders import OrderRepository


@pytest.fixture
def order_path(client):
    customer = client.post(
        "/customers/", json={"name": "Ana", "phone": "35999998888"}
    ).json()
    order = client.post(
        "/orders/",
        json={
            "customer_id": customer["id"],
            "equipment_type": "computer",
            "brand": "Dell",
            "model": "Optiplex",
            "reported_problem": "Não liga",
        },
    ).json()
    return f"/orders/{order['id']}"


def prepare_budget(client, path, amount="123.45"):
    assert client.post(f"{path}/begin-diagnosis").status_code == 200
    assert (
        client.patch(
            f"{path}/diagnosis",
            json={
                "diagnosis": "  Fonte defeituosa  ",
                "budget_amount": amount,
            },
        ).status_code
        == 200
    )
    return client.post(f"{path}/request-approval")


def events(engine, path):
    with Session(engine) as session:
        return list(
            session.scalars(
                select(OrderEvent)
                .where(OrderEvent.order_id == int(path.rsplit("/", 1)[1]))
                .order_by(OrderEvent.id)
            )
        )


@pytest.mark.parametrize("amount", ["0.00", "123.45", "999999.99"])
def test_approval_and_repair_flow_with_persistent_history(
    client, database, order_path, amount
):
    pending = prepare_budget(client, order_path, amount)
    assert pending.status_code == 200
    assert pending.json()["budget_decision"] == "pending"
    assert pending.json()["status"] == "awaiting_approval"
    assert pending.json()["diagnosis"] == "Fonte defeituosa"
    assert client.post(f"{order_path}/start-repair").status_code == 409
    approved = client.post(f"{order_path}/approve-budget")
    assert approved.status_code == 200
    assert approved.json()["budget_decision"] == "approved"
    assert approved.json()["status"] == "awaiting_approval"
    assert client.post(f"{order_path}/approve-budget").status_code == 409
    assert (
        client.post(f"{order_path}/reject-budget", json={"reason": "Custo"}).status_code
        == 409
    )
    assert (
        client.patch(f"{order_path}/diagnosis", json={"budget_amount": "1"}).status_code
        == 409
    )
    repaired = client.post(f"{order_path}/start-repair")
    assert repaired.status_code == 200
    assert repaired.json()["status"] == "in_repair"
    assert client.post(f"{order_path}/start-repair").status_code == 409
    engine = database[0]
    engine.dispose()
    assert client.get(order_path).json() == repaired.json()
    history = events(engine, order_path)
    assert [e.action for e in history] == [
        EventAction.OPEN,
        EventAction.BEGIN_DIAGNOSIS,
        EventAction.REQUEST_APPROVAL,
        EventAction.APPROVE_BUDGET,
        EventAction.START_REPAIR,
    ]
    assert [e.previous_status for e in history] == [
        None,
        OrderStatus.RECEIVED,
        OrderStatus.IN_DIAGNOSIS,
        OrderStatus.AWAITING_APPROVAL,
        OrderStatus.AWAITING_APPROVAL,
    ]
    assert [e.resulting_status for e in history] == [
        OrderStatus.RECEIVED,
        OrderStatus.IN_DIAGNOSIS,
        OrderStatus.AWAITING_APPROVAL,
        OrderStatus.AWAITING_APPROVAL,
        OrderStatus.IN_REPAIR,
    ]
    assert history[3].approved_amount == Decimal(amount)
    assert all(e.created_at.tzinfo for e in history)
    assert client.delete(order_path).status_code == 409


def test_rejection_preserves_reason_and_blocks_further_actions(
    client, database, order_path
):
    assert prepare_budget(client, order_path).status_code == 200
    rejected = client.post(
        f"{order_path}/reject-budget", json={"reason": "  Custo não aprovado  "}
    )
    assert rejected.status_code == 200
    assert rejected.json()["status"] == "cancelled"
    assert rejected.json()["budget_decision"] == "rejected"
    assert rejected.json()["cancellation_reason"] == "Custo não aprovado"
    for action in (
        "begin-diagnosis",
        "request-approval",
        "approve-budget",
        "start-repair",
    ):
        assert client.post(f"{order_path}/{action}").status_code == 409
    assert (
        client.post(f"{order_path}/reject-budget", json={"reason": "Outro"}).status_code
        == 409
    )
    history = events(database[0], order_path)
    assert len(history) == 4
    assert history[-1].action == EventAction.REJECT_BUDGET
    assert history[-1].observation == "Custo não aprovado"
    assert history[-1].resulting_status == OrderStatus.CANCELLED


def test_request_requires_both_fields_and_partial_edits_preserve_values(
    client, database, order_path
):
    assert client.post(f"{order_path}/begin-diagnosis").status_code == 200
    assert client.post(f"{order_path}/begin-diagnosis").status_code == 409
    assert client.post(f"{order_path}/request-approval").status_code == 409
    assert (
        client.patch(f"{order_path}/diagnosis", json={"diagnosis": "Fonte"}).status_code
        == 200
    )
    assert client.post(f"{order_path}/request-approval").status_code == 409
    assert (
        client.patch(f"{order_path}/diagnosis", json={"budget_amount": "10.50"}).json()[
            "diagnosis"
        ]
        == "Fonte"
    )
    assert (
        client.patch(f"{order_path}/diagnosis", json={"diagnosis": None}).json()[
            "budget_amount"
        ]
        == "10.50"
    )
    assert client.post(f"{order_path}/request-approval").status_code == 409
    assert (
        client.patch(
            f"{order_path}/diagnosis",
            json={"diagnosis": "Fonte", "budget_amount": None},
        ).status_code
        == 200
    )
    assert client.post(f"{order_path}/request-approval").status_code == 409
    assert len(events(database[0], order_path)) == 2
    assert client.patch(order_path, json={"brand": "Outra"}).status_code == 409


@pytest.mark.parametrize(
    "body",
    [
        {},
        {"diagnosis": " "},
        {"budget_amount": "-1"},
        {"budget_amount": "0.001"},
        {"budget_amount": "1000000"},
        {"budget_amount": "NaN"},
        {"status": "in_repair"},
        {"budget_decision": "approved"},
    ],
)
def test_invalid_diagnosis_does_not_change_order(client, database, order_path, body):
    client.post(f"{order_path}/begin-diagnosis")
    before = client.get(order_path).json()
    assert client.patch(f"{order_path}/diagnosis", json=body).status_code == 422
    assert client.get(order_path).json() == before
    assert len(events(database[0], order_path)) == 2


@pytest.mark.parametrize(
    "body", [{}, {"reason": " "}, {"reason": None}, {"reason": "x" * 501}]
)
def test_invalid_rejection_preserves_pending_budget(client, database, order_path, body):
    prepare_budget(client, order_path)
    before = client.get(order_path).json()
    assert client.post(f"{order_path}/reject-budget", json=body).status_code == 422
    assert client.get(order_path).json() == before
    assert len(events(database[0], order_path)) == 3


@pytest.mark.parametrize(
    "action,method,body",
    [
        ("begin-diagnosis", "post", None),
        ("diagnosis", "patch", {"diagnosis": "Fonte"}),
        ("request-approval", "post", None),
        ("approve-budget", "post", None),
        ("reject-budget", "post", {"reason": "Custo"}),
        ("start-repair", "post", None),
    ],
)
def test_missing_order_returns_404(client, action, method, body):
    assert (
        client.request(method, f"/orders/999999/{action}", json=body).status_code == 404
    )


@pytest.mark.parametrize("status", list(OrderStatus))
def test_actions_reject_wrong_status_without_events(
    client, database, order_path, status
):
    with Session(database[0]) as session:
        order = session.get(ServiceOrder, int(order_path.rsplit("/", 1)[1]))
        order.status = status
        order.budget_decision = BudgetDecision.NOT_REQUESTED
        session.commit()
    if status != OrderStatus.RECEIVED:
        assert client.post(f"{order_path}/begin-diagnosis").status_code == 409
    if status != OrderStatus.IN_DIAGNOSIS:
        assert (
            client.patch(
                f"{order_path}/diagnosis", json={"diagnosis": "Fonte"}
            ).status_code
            == 409
        )
    for action in ("request-approval", "approve-budget", "start-repair"):
        assert client.post(f"{order_path}/{action}").status_code == 409
    assert (
        client.post(f"{order_path}/reject-budget", json={"reason": "Custo"}).status_code
        == 409
    )
    assert len(events(database[0], order_path)) == 1


@pytest.mark.parametrize(
    "action",
    [
        "begin-diagnosis",
        "request-approval",
        "approve-budget",
        "reject-budget",
        "start-repair",
    ],
)
def test_event_failure_rolls_back_action(
    client, database, order_path, monkeypatch, action
):
    if action != "begin-diagnosis":
        prepare_budget(client, order_path)
    if action == "request-approval":
        with Session(database[0]) as session:
            session.get(
                ServiceOrder, int(order_path.rsplit("/", 1)[1])
            ).status = OrderStatus.IN_DIAGNOSIS
            session.commit()
    if action == "start-repair":
        client.post(f"{order_path}/approve-budget")
    before = client.get(order_path).json()
    count = len(events(database[0], order_path))
    original = OrderRepository.add_event

    def invalid_event(self, order, event_action, previous_status, **kwargs):
        original(self, order, event_action, previous_status, **kwargs)
        self.session.add(
            OrderEvent(order_id=order.id, action=event_action, resulting_status=None)
        )
        self.session.flush()

    monkeypatch.setattr(OrderRepository, "add_event", invalid_event)
    with pytest.raises(IntegrityError):
        client.post(
            f"{order_path}/{action}",
            **({"json": {"reason": "Custo"}} if action == "reject-budget" else {}),
        )
    assert client.get(order_path).json() == before
    assert len(events(database[0], order_path)) == count
