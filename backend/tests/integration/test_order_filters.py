from sqlalchemy.orm import Session

from src.models import ServiceOrder
from src.models.enums import BudgetDecision, OrderStatus


def test_filters_and_live_summary(client, database):
    assert client.get("/orders/summary").json() == {
        "open": 0,
        "awaiting_approval": 0,
        "ready_for_delivery": 0,
    }
    ids = []
    for name in ["Ana % Silva", "Bia"]:
        customer = client.post(
            "/customers/", json={"name": name, "phone": "35999998888"}
        ).json()
        ids.append(
            client.post(
                "/orders/",
                json={
                    "customer_id": customer["id"],
                    "equipment_type": "notebook",
                    "brand": "Dell",
                    "model": "X",
                    "reported_problem": "Não liga",
                },
            ).json()["id"]
        )
    assert [o["id"] for o in client.get("/orders/?customer=ANA%20%25").json()] == ids[
        :1
    ]
    assert client.get(f"/orders/?order_id={ids[0]}&customer=Bia").json() == []
    assert client.get("/orders/?status=completed").json() == []
    assert len(client.get("/orders/?status=received&limit=1&offset=1").json()) == 1
    engine, _ = database
    with Session(engine) as session:
        first = session.get(ServiceOrder, ids[0])
        first.status = OrderStatus.AWAITING_APPROVAL
        first.budget_decision = BudgetDecision.PENDING
        second = session.get(ServiceOrder, ids[1])
        second.status = OrderStatus.COMPLETED
        session.commit()
    assert client.get("/orders/summary").json() == {
        "open": 2,
        "awaiting_approval": 1,
        "ready_for_delivery": 1,
    }
    with Session(engine) as session:
        session.get(ServiceOrder, ids[0]).budget_decision = BudgetDecision.APPROVED
        session.get(ServiceOrder, ids[1]).status = OrderStatus.DELIVERED
        session.commit()
    assert client.get("/orders/summary").json() == {
        "open": 1,
        "awaiting_approval": 0,
        "ready_for_delivery": 0,
    }
    for query in ["order_id=0", "status=invalid", "customer=" + "x" * 101]:
        assert client.get("/orders/?" + query).status_code == 422
