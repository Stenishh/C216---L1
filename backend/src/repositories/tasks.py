from threading import RLock

from src.schemas.tasks import Task, TaskCreate


class TaskNotFound(Exception):
    pass


class TaskRepository:
    """Armazenamento por processo; operacoes atomicas entre threads."""

    def __init__(self):
        self._tasks: dict[int, Task] = {}
        self._next_id = 1
        self._lock = RLock()

    def create(self, data: TaskCreate) -> Task:
        with self._lock:
            task = Task(id=self._next_id, **data.model_dump())
            self._tasks[task.id] = task
            self._next_id += 1
            return task

    def get(self, task_id: int) -> Task:
        with self._lock:
            if task_id not in self._tasks:
                raise TaskNotFound(task_id)
            return self._tasks[task_id]

    def list(self) -> list[Task]:
        with self._lock:
            return list(self._tasks.values())

    def update(self, task_id: int, changes: dict) -> Task:
        with self._lock:
            current = self.get(task_id)
            task = Task.model_validate(current.model_dump() | changes)
            self._tasks[task_id] = task
            return task

    def delete(self, task_id: int) -> None:
        with self._lock:
            self.get(task_id)
            del self._tasks[task_id]
