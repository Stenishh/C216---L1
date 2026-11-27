from fastapi import APIRouter

from src.schemas.health import HealthRead

router = APIRouter(tags=["Saude"])


@router.get("/health", response_model=HealthRead)
def health() -> HealthRead:
    """Confirma que a API responde, sem verificar dependencias externas."""
    return HealthRead(status="ok", service="repara")
