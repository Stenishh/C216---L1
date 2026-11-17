from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models import Customer, OrderEvent, ServiceOrder
from src.models.enums import EventAction, OrderStatus
from src.schemas.orders import OrderCreate


class OrderRepository:
    def __init__(self, session: Session):
        self.session = session

    def get(self, order_id: int, *, lock: bool = False) -> ServiceOrder | None:
        statement = select(ServiceOrder).where(ServiceOrder.id == order_id)
        if lock:
            statement = statement.with_for_update()
        return self.session.scalar(statement)

    def customer_exists(self, customer_id: int) -> bool:
        return self.session.get(Customer, customer_id) is not None

    def list(self, offset: int, limit: int) -> list[ServiceOrder]:
        return list(
            self.session.scalars(
                select(ServiceOrder)
                .order_by(ServiceOrder.created_at.desc(), ServiceOrder.id.desc())
                .offset(offset)
                .limit(limit)
            )
        )

    def create(self, data: OrderCreate) -> ServiceOrder:
        order = ServiceOrder(**data.model_dump())
        order.events.append(
            OrderEvent(
                action=EventAction.OPEN,
                previous_status=None,
                resulting_status=OrderStatus.RECEIVED,
            )
        )
        self.session.add(order)
        self.session.flush()
        return order

    def update(self, order: ServiceOrder, values: dict) -> ServiceOrder:
        for field, value in values.items():
            setattr(order, field, value)
        self.session.flush()
        return order

    def has_only_open_event(self, order_id: int) -> bool:
        events = list(
            self.session.scalars(
                select(OrderEvent).where(OrderEvent.order_id == order_id).limit(2)
            )
        )
        return (
            len(events) == 1
            and events[0].action == EventAction.OPEN
            and events[0].previous_status is None
            and events[0].resulting_status == OrderStatus.RECEIVED
        )

    def delete(self, order: ServiceOrder) -> None:
        self.session.delete(order)
        self.session.flush()

    def add_event(
        self,
        order: ServiceOrder,
        action: EventAction,
        previous_status: OrderStatus,
        *,
        observation: str | None = None,
        approved_amount=None,
    ) -> None:
        self.session.add(
            OrderEvent(
                order_id=order.id,
                action=action,
                previous_status=previous_status,
                resulting_status=order.status,
                observation=observation,
                approved_amount=approved_amount,
            )
        )
        self.session.flush()
