import os
from datetime import timedelta
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

import pytest
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from sqlalchemy import create_engine, delete, func, inspect, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.schema import CreateSchema, DropSchema

from alembic import command
from src.models import Customer, OrderEvent, ServiceOrder
from src.models.enums import BudgetDecision, EquipmentType, EventAction, OrderStatus


@pytest.fixture
def database():
    url = os.getenv("TEST_DATABASE_URL")
    if not url:
        pytest.skip("Use make test-postgres para executar em banco isolado.")
    # Schema aleatorio: nenhuma migration e aplicada ao schema public.
    schema = f"repara_test_{uuid4().hex}"
    admin = create_engine(url, hide_parameters=True)
    with admin.begin() as connection:
        connection.execute(CreateSchema(schema))
    engine = create_engine(
        url,
        connect_args={"options": f"-csearch_path={schema} -ctimezone=UTC"},
        hide_parameters=True,
    )
    config = Config(str(Path(__file__).resolve().parents[2] / "alembic.ini"))
    try:
        with engine.begin() as connection:
            config.attributes["connection"] = connection
            command.upgrade(config, "head")
        yield engine, config
    finally:
        engine.dispose()
        with admin.begin() as connection:
            connection.execute(DropSchema(schema, cascade=True))
        admin.dispose()


def create_order(session):
    customer = Customer(name="Ana", phone="35999998888")
    order = ServiceOrder(
        customer=customer,
        equipment_type=EquipmentType.NOTEBOOK,
        brand="Marca",
        model="Modelo",
        reported_problem="Nao liga",
        budget_amount=Decimal("123.45"),
    )
    order.events.append(
        OrderEvent(
            action=EventAction.OPEN,
            resulting_status=OrderStatus.RECEIVED,
        )
    )
    session.add(order)
    session.commit()
    return customer.id, order.id


def test_migration_is_at_head_and_matches_models(database):
    engine, config = database
    assert set(inspect(engine).get_table_names()) == {
        "alembic_version",
        "customers",
        "service_orders",
        "order_events",
    }
    with engine.begin() as connection:
        assert MigrationContext.configure(connection).get_current_revision() == "0001"
        config.attributes["connection"] = connection
        command.check(config)


def test_data_and_history_survive_new_connection(database):
    engine, _ = database
    with Session(engine) as session:
        customer_id, order_id = create_order(session)
    engine.dispose()
    with Session(engine) as session:
        order = session.get(ServiceOrder, order_id)
        assert order.customer.id == customer_id
        assert order.customer.name == "Ana"
        assert order.budget_amount == Decimal("123.45")
        assert order.status == OrderStatus.RECEIVED
        assert order.budget_decision == BudgetDecision.NOT_REQUESTED
        assert order.created_at.utcoffset() == timedelta(0)
        assert len(order.events) == 1
        assert order.events[0].action == EventAction.OPEN
        assert order.events[0].previous_status is None


def test_customer_with_order_cannot_be_deleted(database):
    engine, _ = database
    with Session(engine) as session:
        customer_id, _ = create_order(session)
        with pytest.raises(IntegrityError):
            session.execute(delete(Customer).where(Customer.id == customer_id))
            session.commit()
        session.rollback()
        assert session.get(Customer, customer_id) is not None


def test_deleting_order_removes_its_events_but_keeps_customer(database):
    engine, _ = database
    with Session(engine) as session:
        customer_id, order_id = create_order(session)
        session.execute(delete(ServiceOrder).where(ServiceOrder.id == order_id))
        session.commit()
        assert session.scalar(select(func.count()).select_from(OrderEvent)) == 0
        assert session.get(Customer, customer_id) is not None


@pytest.mark.parametrize(
    "assignment",
    [
        "budget_amount = -1",
        "status = 'unknown'",
        "equipment_type = 'phone'",
        "budget_decision = 'unknown'",
        "brand = '   '",
    ],
)
def test_database_rejects_invalid_order_values(database, assignment):
    engine, _ = database
    with Session(engine) as session:
        _, order_id = create_order(session)
        with pytest.raises(IntegrityError):
            # assignment vem apenas dos casos fixos deste teste.
            session.execute(
                text(f"UPDATE service_orders SET {assignment} WHERE id = :id"),
                {"id": order_id},
            )
            session.commit()
        session.rollback()
        assert session.get(ServiceOrder, order_id).status == OrderStatus.RECEIVED


@pytest.mark.parametrize("phone", ["123", "3599999abcd"])
def test_database_rejects_invalid_customer_phone(database, phone):
    engine, _ = database
    with Session(engine) as session:
        session.add(Customer(name="Ana", phone=phone))
        with pytest.raises(IntegrityError):
            session.commit()


def test_order_requires_existing_customer(database):
    engine, _ = database
    with Session(engine) as session:
        session.add(
            ServiceOrder(
                customer_id=999999,
                equipment_type=EquipmentType.COMPUTER,
                brand="Marca",
                model="Modelo",
                reported_problem="Nao liga",
            )
        )
        with pytest.raises(IntegrityError):
            session.commit()


def test_downgrade_and_reupgrade_in_disposable_schema(database):
    engine, config = database
    with engine.begin() as connection:
        config.attributes["connection"] = connection
        command.downgrade(config, "base")
        assert set(inspect(connection).get_table_names()) == {"alembic_version"}
        assert MigrationContext.configure(connection).get_current_revision() is None
        command.upgrade(config, "head")
        assert MigrationContext.configure(connection).get_current_revision() == "0001"
        command.check(config)
