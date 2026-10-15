from fastapi import FastAPI

from src.repositories.tasks import TaskRepository
from src.routers import system, tasks

app = FastAPI(
    title="C216 L1 - Backend",
    description="Backend do laboratorio de Sistemas Distribuidos",
    version="0.1.0",
)


app.state.task_repository = TaskRepository()
app.include_router(system.router)
app.include_router(tasks.router)
