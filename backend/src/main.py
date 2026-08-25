from fastapi import FastAPI

app = FastAPI(
    title="C216 L1 - Backend",
    description="Backend do laboratorio de Sistemas Distribuidos",
    version="0.1.0",
)


@app.get("/health")
def health():
    return {"service": "backend", "state": "up"}


@app.get("/info")
def info():
    return {
        "disciplina": "C216 - Sistemas Distribuidos",
        "instituicao": "INATEL",
        "periodo": "2026.2",
        "versao": app.version,
    }
