import re
from datetime import datetime
from typing import Annotated

from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    EmailStr,
    Field,
    model_validator,
)


def normalize_phone(value):
    if isinstance(value, str):
        return re.sub(r"[()\s-]", "", value)
    return value


def optional_email(value):
    if isinstance(value, str) and not value.strip():
        return None
    return value


Name = Annotated[str, Field(min_length=1, max_length=100)]
Phone = Annotated[
    str, BeforeValidator(normalize_phone), Field(pattern=r"^[0-9]{10,11}$")
]
EmailValue = Annotated[EmailStr, Field(max_length=254)]
Email = Annotated[EmailValue | None, BeforeValidator(optional_email)]


class CustomerCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    name: Name
    phone: Phone
    email: Email = None


class CustomerPatch(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    name: Name | None = None
    phone: Phone | None = None
    email: Email = None

    @model_validator(mode="after")
    def validate_changes(self):
        if not self.model_fields_set:
            raise ValueError("Informe pelo menos um campo para atualizar.")
        for field in ("name", "phone"):
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(f"O campo {field} não pode ser nulo.")
        return self


class CustomerRead(CustomerCreate):
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)
    id: int
    created_at: datetime
