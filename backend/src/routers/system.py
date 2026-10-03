from fastapi import APIRouter, Request

router = APIRouter(tags=["Sistema"])


@router.get("/health")
def health():
    return {"service": "backend", "state": "up"}


@router.get("/info")
def info(request: Request):
    return {
        "disciplina": "C216 - Sistemas Distribuidos",
        "instituicao": "INATEL",
        "periodo": "2026.2",
        "versao": request.app.version,
    }
