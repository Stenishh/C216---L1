from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Response, status

from src.dependencies import get_task_service
from src.repositories.tasks import TaskNotFound
from src.schemas.tasks import Task, TaskCreate, TaskPatch, TaskReplace
from src.services.tasks import TaskService

router = APIRouter(prefix="/tasks", tags=["Tarefas"])
Service = Annotated[TaskService, Depends(get_task_service)]
TaskId = Annotated[int, Path(gt=0)]


def existing_task(task_id: TaskId, service: Service) -> Task:
    try:
        return service.get(task_id)
    except TaskNotFound as exc:
        raise HTTPException(404, "Tarefa nao encontrada") from exc


ExistingTask = Annotated[Task, Depends(existing_task)]


@router.get("", response_model=list[Task])
def list_tasks(
    service: Service,
    completed: bool | None = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    return service.list(completed, offset, limit)


@router.post("", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(data: TaskCreate, service: Service, response: Response):
    task = service.create(data)
    response.headers["Location"] = f"/tasks/{task.id}"
    return task


@router.get("/{task_id}", response_model=Task)
def get_task(task: ExistingTask):
    return task


@router.put("/{task_id}", response_model=Task)
def replace_task(task: ExistingTask, data: TaskReplace, service: Service):
    try:
        return service.replace(task.id, data)
    except TaskNotFound as exc:
        raise HTTPException(404, "Tarefa nao encontrada") from exc


@router.patch("/{task_id}", response_model=Task)
def patch_task(task: ExistingTask, data: TaskPatch, service: Service):
    try:
        return service.patch(task.id, data)
    except TaskNotFound as exc:
        raise HTTPException(404, "Tarefa nao encontrada") from exc


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task: ExistingTask, service: Service):
    try:
        service.delete(task.id)
    except TaskNotFound as exc:
        raise HTTPException(404, "Tarefa nao encontrada") from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)
