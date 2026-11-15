from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import CORS_ORIGINS
from src.routers import items, system, tasks

app = FastAPI(
    title="C216 L1 - Backend",
    description="Backend do laboratorio de Sistemas Distribuidos",
    version="0.1.0",
)


app.include_router(system.router)
app.include_router(tasks.router)
app.include_router(items.router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)
