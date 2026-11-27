from enum import StrEnum

from sqlalchemy import Enum


class EquipmentType(StrEnum):
    COMPUTER = "computer"
    NOTEBOOK = "notebook"


class OrderStatus(StrEnum):
    RECEIVED = "received"
    IN_DIAGNOSIS = "in_diagnosis"
    AWAITING_APPROVAL = "awaiting_approval"
    IN_REPAIR = "in_repair"
    COMPLETED = "completed"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class BudgetDecision(StrEnum):
    NOT_REQUESTED = "not_requested"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class EventAction(StrEnum):
    OPEN = "open"
    BEGIN_DIAGNOSIS = "begin_diagnosis"
    REQUEST_APPROVAL = "request_approval"
    APPROVE_BUDGET = "approve_budget"
    REJECT_BUDGET = "reject_budget"
    START_REPAIR = "start_repair"
    COMPLETE_REPAIR = "complete_repair"
    DELIVER = "deliver"
    CANCEL = "cancel"


def enum_column(enum_class: type[StrEnum], name: str) -> Enum:
    return Enum(
        enum_class,
        name=name,
        native_enum=False,
        create_constraint=True,
        validate_strings=True,
        values_callable=lambda values: [value.value for value in values],
    )
