from decimal import Decimal

import pytest
from pydantic import ValidationError

from src.schemas.orders import BudgetRejection, DiagnosisPatch


@pytest.mark.parametrize("amount", ["0", "0.01", "123.45", "999999.99", 10, 1.25])
def test_valid_budget_is_decimal(amount):
    data = DiagnosisPatch(budget_amount=amount)
    assert isinstance(data.budget_amount, Decimal)
    assert data.budget_amount == Decimal(str(amount))


@pytest.mark.parametrize(
    "amount", ["-0.01", "1000000", "0.001", "NaN", "Infinity", True, "abc"]
)
def test_invalid_budget_is_rejected(amount):
    with pytest.raises(ValidationError):
        DiagnosisPatch(budget_amount=amount)


@pytest.mark.parametrize(
    "body",
    [
        {},
        {"diagnosis": " "},
        {"diagnosis": "x" * 2001},
        {"status": "in_repair"},
        {"budget_decision": "approved"},
    ],
)
def test_invalid_diagnosis_patch(body):
    with pytest.raises(ValidationError):
        DiagnosisPatch(**body)


def test_optional_diagnosis_fields_can_be_cleared_explicitly():
    assert DiagnosisPatch(diagnosis=None).model_dump(exclude_unset=True) == {
        "diagnosis": None
    }
    assert DiagnosisPatch(budget_amount=None).model_dump(exclude_unset=True) == {
        "budget_amount": None
    }
    assert (
        DiagnosisPatch(diagnosis="  Fonte defeituosa  ").diagnosis == "Fonte defeituosa"
    )


@pytest.mark.parametrize(
    "body",
    [
        {},
        {"reason": " "},
        {"reason": None},
        {"reason": "x" * 501},
        {"reason": "Custo", "status": "cancelled"},
    ],
)
def test_rejection_requires_valid_reason(body):
    with pytest.raises(ValidationError):
        BudgetRejection(**body)
