from src.repositories.tasks import TaskRepository
from src.schemas.tasks import Task, TaskCreate, TaskPatch, TaskReplace


class TaskService:
    def __init__(self, repository: TaskRepository):
        self.repository = repository

    def create(self, data: TaskCreate) -> Task:
        return self.repository.create(data)

    def get(self, task_id: int) -> Task:
        return self.repository.get(task_id)

    def list(self, completed: bool | None, offset: int, limit: int) -> list[Task]:
        return self.repository.list(completed, offset, limit)

    def replace(self, task_id: int, data: TaskReplace) -> Task:
        return self.repository.update(task_id, data.model_dump())

    def patch(self, task_id: int, data: TaskPatch) -> Task:
        return self.repository.update(task_id, data.model_dump(exclude_unset=True))

    def delete(self, task_id: int) -> None:
        self.repository.delete(task_id)
