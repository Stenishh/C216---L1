from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Identity,
    Numeric,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base
from src.models.enums import EventAction, OrderStatus, enum_column

if TYPE_CHECKING:
    from src.models.service_order import ServiceOrder


class OrderEvent(Base):
    __tablename__ = "order_events"
    __table_args__ = (
        CheckConstraint(
            "approved_amount IS NULL OR approved_amount BETWEEN 0 AND 999999.99",
            name="approved_amount_range",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("service_orders.id", ondelete="CASCADE"), index=True
    )
    action: Mapped[EventAction] = mapped_column(
        enum_column(EventAction, "event_action")
    )
    previous_status: Mapped[OrderStatus | None] = mapped_column(
        enum_column(OrderStatus, "previous_status")
    )
    resulting_status: Mapped[OrderStatus] = mapped_column(
        enum_column(OrderStatus, "resulting_status")
    )
    observation: Mapped[str | None] = mapped_column(String(2000))
    approved_amount: Mapped[Decimal | None] = mapped_column(Numeric(8, 2))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    order: Mapped[ServiceOrder] = relationship(back_populates="events")
