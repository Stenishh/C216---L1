from fastapi import Request

from src.services.tasks import TaskService


def get_task_service(request: Request) -> TaskService:
    return TaskService(request.app.state.task_repository)
