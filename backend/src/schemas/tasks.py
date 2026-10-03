from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, model_validator

Title = Annotated[str, Field(min_length=1, max_length=120)]
Description = Annotated[str, Field(max_length=1000)]


class TaskCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    title: Title
    description: Description = ""
    completed: bool = False


class TaskReplace(TaskCreate):
    description: Description
    completed: bool


class TaskPatch(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    title: Title | None = None
    description: Description | None = None
    completed: bool | None = None

    @model_validator(mode="after")
    def validate_changes(self):
        if not self.model_fields_set:
            raise ValueError("Envie pelo menos um campo para atualizar")
        if any(getattr(self, field) is None for field in self.model_fields_set):
            raise ValueError("Os campos enviados nao podem ser nulos")
        return self


class Task(TaskCreate):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, frozen=True)
    id: int = Field(gt=0)
