from datetime import datetime
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, model_validator

from src.models.enums import BudgetDecision, EquipmentType, EventAction, OrderStatus

ShortText = Annotated[str, Field(min_length=1, max_length=100)]
Problem = Annotated[str, Field(min_length=1, max_length=2000)]
CustomerId = Annotated[int, Field(gt=0, strict=True)]
BudgetAmount = Annotated[
    Decimal, Field(ge=0, le=Decimal("999999.99"), max_digits=8, decimal_places=2)
]


class DiagnosisPatch(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    diagnosis: Problem | None = None
    budget_amount: BudgetAmount | None = None

    @model_validator(mode="after")
    def validate_changes(self):
        if not self.model_fields_set:
            raise ValueError("Informe diagnóstico ou orçamento para atualizar.")
        return self


class BudgetRejection(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    reason: Annotated[str, Field(min_length=1, max_length=500)]


class OrderCancellation(BudgetRejection):
    pass


class RepairPatch(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    service_performed: Problem | None


class DeliveryConfirmation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    confirmed: Annotated[bool, Field(strict=True)]

    @model_validator(mode="after")
    def require_confirmation(self):
        if not self.confirmed:
            raise ValueError("Confirme a entrega do equipamento.")
        return self


class OrderEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int
    action: EventAction
    previous_status: OrderStatus | None
    resulting_status: OrderStatus
    observation: str | None
    approved_amount: Decimal | None
    created_at: datetime


class OrderCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    customer_id: CustomerId
    equipment_type: EquipmentType
    brand: ShortText
    model: ShortText
    serial_number: Annotated[str, Field(max_length=100)] | None = None
    reported_problem: Problem


class OrderPatch(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    customer_id: CustomerId | None = None
    equipment_type: EquipmentType | None = None
    brand: ShortText | None = None
    model: ShortText | None = None
    serial_number: Annotated[str, Field(max_length=100)] | None = None
    reported_problem: Problem | None = None

    @model_validator(mode="after")
    def validate_changes(self):
        if not self.model_fields_set:
            raise ValueError("Informe pelo menos um campo para atualizar.")
        for field in self.model_fields_set - {"serial_number"}:
            if getattr(self, field) is None:
                raise ValueError(f"O campo {field} não pode ser nulo.")
        return self


class OrderRead(OrderCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    diagnosis: str | None
    budget_amount: Decimal | None
    budget_decision: BudgetDecision
    service_performed: str | None
    cancellation_reason: str | None
    status: OrderStatus
    created_at: datetime
    updated_at: datetime
