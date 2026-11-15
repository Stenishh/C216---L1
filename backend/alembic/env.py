from sqlalchemy import create_engine, pool

from alembic import context
from src.core.config import get_database_url
from src.database.base import Base
from src.models import Customer, OrderEvent, ServiceOrder  # noqa: F401

target_metadata = Base.metadata


def configure(connection):
    context.configure(
        connection=connection, target_metadata=target_metadata, compare_type=True
    )
    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    context.configure(
        url=get_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()
elif connection := context.config.attributes.get("connection"):
    configure(connection)
else:
    engine = create_engine(
        get_database_url(),
        poolclass=pool.NullPool,
        hide_parameters=True,
        connect_args={"options": "-c timezone=UTC"},
    )
    with engine.connect() as connection:
        configure(connection)
    engine.dispose()
