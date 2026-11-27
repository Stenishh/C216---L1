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
    Index,
    Numeric,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base
from src.models.enums import BudgetDecision, EquipmentType, OrderStatus, enum_column

if TYPE_CHECKING:
    from src.models.customer import Customer
    from src.models.order_event import OrderEvent


class ServiceOrder(Base):
    __tablename__ = "service_orders"
    __table_args__ = (
        CheckConstraint("length(trim(brand)) BETWEEN 1 AND 100", name="brand_length"),
        CheckConstraint("length(trim(model)) BETWEEN 1 AND 100", name="model_length"),
        CheckConstraint(
            "length(trim(reported_problem)) BETWEEN 1 AND 2000",
            name="reported_problem_length",
        ),
        CheckConstraint(
            "budget_amount IS NULL OR budget_amount BETWEEN 0 AND 999999.99",
            name="budget_range",
        ),
        CheckConstraint(
            "cancellation_reason IS NULL OR length(trim(cancellation_reason)) BETWEEN 1 AND 500",
            name="cancellation_reason_length",
        ),
        Index("ix_service_orders_status_created_at", "status", "created_at"),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id", ondelete="RESTRICT"), index=True
    )
    equipment_type: Mapped[EquipmentType] = mapped_column(
        enum_column(EquipmentType, "equipment_type")
    )
    brand: Mapped[str] = mapped_column(String(100))
    model: Mapped[str] = mapped_column(String(100))
    serial_number: Mapped[str | None] = mapped_column(String(100))
    reported_problem: Mapped[str] = mapped_column(String(2000))
    diagnosis: Mapped[str | None] = mapped_column(String(2000))
    budget_amount: Mapped[Decimal | None] = mapped_column(Numeric(8, 2))
    budget_decision: Mapped[BudgetDecision] = mapped_column(
        enum_column(BudgetDecision, "budget_decision"), server_default="not_requested"
    )
    service_performed: Mapped[str | None] = mapped_column(String(2000))
    cancellation_reason: Mapped[str | None] = mapped_column(String(500))
    status: Mapped[OrderStatus] = mapped_column(
        enum_column(OrderStatus, "order_status"), server_default="received"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    customer: Mapped[Customer] = relationship(back_populates="orders")
    events: Mapped[list[OrderEvent]] = relationship(
        back_populates="order", passive_deletes="all", order_by="OrderEvent.id"
    )
