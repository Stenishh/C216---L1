from collections.abc import Generator
from functools import lru_cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session

from src.core.config import get_database_url


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    return create_engine(
        get_database_url(),
        pool_pre_ping=True,
        hide_parameters=True,
        connect_args={"options": "-c timezone=UTC"},
    )


def get_db() -> Generator[Session]:
    with Session(get_engine(), expire_on_commit=False) as session:
        try:
            yield session
        except Exception:
            session.rollback()
            raise
