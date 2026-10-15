from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from src.database.session import get_db
from src.repositories.tasks import TaskRepository
from src.services.tasks import TaskService


def get_task_service(db: Annotated[Session, Depends(get_db)]) -> TaskService:
    return TaskService(TaskRepository(db))
