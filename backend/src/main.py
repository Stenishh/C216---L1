from fastapi import FastAPI

from src.routers.customers import router as customers_router
from src.routers.health import router as health_router

app = FastAPI(
    title="Repara API",
    description="Gestao de ordens de servico de assistencia tecnica.",
    version="0.1.0",
)
app.include_router(health_router)
app.include_router(customers_router)
