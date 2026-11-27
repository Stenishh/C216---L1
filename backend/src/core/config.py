import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy.engine import make_url

load_dotenv(Path(__file__).resolve().parents[3] / ".env")


def get_database_url() -> str:
    value = os.getenv("DATABASE_URL", "").strip()
    if not value:
        raise RuntimeError("Configure DATABASE_URL no ambiente ou no arquivo .env.")
    try:
        url = make_url(value)
        valid = url.drivername == "postgresql+psycopg" and bool(url.database)
    except Exception:
        valid = False
    if not valid:
        raise ValueError("DATABASE_URL deve indicar um banco PostgreSQL com psycopg.")
    return value
