from datetime import datetime
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, model_validator

from src.models.enums import BudgetDecision, EquipmentType, OrderStatus

ShortText = Annotated[str, Field(min_length=1, max_length=100)]
Problem = Annotated[str, Field(min_length=1, max_length=2000)]
CustomerId = Annotated[int, Field(gt=0, strict=True)]


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
