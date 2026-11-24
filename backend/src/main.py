import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.routers.customers import router as customers_router
from src.routers.health import router as health_router
from src.routers.orders import router as orders_router

app = FastAPI(
    title="Repara API",
    description="Gestao de ordens de servico de assistencia tecnica.",
    version="0.1.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS", "http://127.0.0.1:5173,http://localhost:5173"
        ).split(",")
        if origin.strip()
    ],
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Content-Type", "Accept"],
)
app.include_router(health_router)
app.include_router(customers_router)
app.include_router(orders_router)
