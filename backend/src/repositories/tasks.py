from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.tasks import TaskModel
from src.schemas.tasks import Task, TaskCreate


class TaskNotFound(Exception):
    pass


class TaskRepository:
    """Acesso persistente às tarefas usando a sessão da requisição."""

    def __init__(self, db: Session):
        self.db = db

    def _get_model(self, task_id: int) -> TaskModel:
        task = self.db.get(TaskModel, task_id)
        if task is None:
            raise TaskNotFound(task_id)
        return task

    def create(self, data: TaskCreate) -> Task:
        task = TaskModel(**data.model_dump())
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return Task.model_validate(task)

    def get(self, task_id: int) -> Task:
        return Task.model_validate(self._get_model(task_id))

    def list(
        self, completed: bool | None = None, offset: int = 0, limit: int = 100
    ) -> list[Task]:
        query = select(TaskModel).order_by(TaskModel.id)
        if completed is not None:
            query = query.where(TaskModel.completed == completed)
        tasks = self.db.scalars(query.offset(offset).limit(limit)).all()
        return [Task.model_validate(task) for task in tasks]

    def update(self, task_id: int, changes: dict) -> Task:
        task = self._get_model(task_id)
        for field, value in changes.items():
            setattr(task, field, value)
        self.db.commit()
        self.db.refresh(task)
        return Task.model_validate(task)

    def delete(self, task_id: int) -> None:
        self.db.delete(self._get_model(task_id))
        self.db.commit()
