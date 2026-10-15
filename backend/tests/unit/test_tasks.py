import pytest
from pydantic import ValidationError

from src.repositories.tasks import TaskNotFound, TaskRepository
from src.schemas.tasks import TaskCreate, TaskPatch, TaskReplace
from src.services.tasks import TaskService


@pytest.fixture
def service():
    return TaskService(TaskRepository())


def test_ids_are_not_reused(service):
    first = service.create(TaskCreate(title="Primeira"))
    service.delete(first.id)
    second = service.create(TaskCreate(title="Segunda"))
    assert second.id > first.id


def test_replace_and_patch(service):
    task = service.create(TaskCreate(title="Original", description="Descricao"))
    patched = service.patch(task.id, TaskPatch(completed=True))
    assert patched.description == "Descricao"
    assert patched.completed is True
    replaced = service.replace(
        task.id, TaskReplace(title="Nova", description="", completed=False)
    )
    assert replaced.description == ""
    assert replaced.id == task.id
    assert replaced.completed is False


def test_filter_before_pagination(service):
    for index in range(5):
        service.create(TaskCreate(title=str(index), completed=index % 2 == 0))
    assert [task.title for task in service.list(True, 1, 1)] == ["2"]
    assert len(service.list(None, 0, 20)) == 5


def test_repository_instances_are_isolated(service):
    service.create(TaskCreate(title="Tarefa"))
    assert TaskRepository().list() == []


def test_results_cannot_mutate_storage(service):
    task = service.create(TaskCreate(title="Original"))
    with pytest.raises(ValidationError):
        task.title = "Alterada"
    tasks = service.repository.list()
    tasks.clear()
    assert service.get(task.id).title == "Original"


@pytest.mark.parametrize("operation", ["get", "delete", "replace", "patch"])
def test_missing_task(service, operation):
    with pytest.raises(TaskNotFound):
        if operation == "replace":
            service.replace(
                1, TaskReplace(title="Nova", description="", completed=False)
            )
        elif operation == "patch":
            service.patch(1, TaskPatch(completed=True))
        else:
            getattr(service, operation)(1)


@pytest.mark.parametrize("payload", [{}, {"title": None}, {"title": " "}, {"id": 1}])
def test_patch_validation(payload):
    with pytest.raises(ValidationError):
        TaskPatch(**payload)
