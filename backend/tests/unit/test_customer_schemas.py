import pytest
from pydantic import ValidationError

from src.schemas.customers import CustomerCreate, CustomerPatch


def test_create_normalizes_name_phone_and_email():
    data = CustomerCreate(
        name="  Ana Silva  ", phone="(35) 99999-8888", email="ana@EXAMPLE.COM"
    )
    assert data.model_dump() == {
        "name": "Ana Silva",
        "phone": "35999998888",
        "email": "ana@example.com",
    }


@pytest.mark.parametrize("email", [None, "", "   "])
def test_optional_email_can_be_empty(email):
    assert CustomerCreate(name="Ana", phone="3534721234", email=email).email is None


@pytest.mark.parametrize(
    "changes",
    [
        {"name": ""},
        {"name": " \n "},
        {"name": "a" * 101},
        {"name": None},
        {"phone": "123"},
        {"phone": "35abc998888"},
        {"phone": None},
        {"phone": 35999998888},
        {"email": "invalido"},
        {"id": 1},
    ],
)
def test_create_rejects_invalid_fields(changes):
    body = {"name": "Ana", "phone": "35999998888", **changes}
    with pytest.raises(ValidationError):
        CustomerCreate(**body)


@pytest.mark.parametrize("body", [{}, {"name": None}, {"phone": None}, {"unknown": 1}])
def test_patch_rejects_empty_null_required_fields_and_unknown_fields(body):
    with pytest.raises(ValidationError):
        CustomerPatch(**body)


def test_patch_distinguishes_omitted_email_from_clear_email():
    assert CustomerPatch(name="Novo nome").model_dump(exclude_unset=True) == {
        "name": "Novo nome"
    }
    assert CustomerPatch(email=None).model_dump(exclude_unset=True) == {"email": None}
