from sqlalchemy import Boolean, String, text
from sqlalchemy.orm import Mapped, mapped_column

from src.database.base import Base


class TaskModel(Base):
    __tablename__ = "tasks"
    __table_args__ = {"sqlite_autoincrement": True}

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(String(1000), server_default="")
    completed: Mapped[bool] = mapped_column(Boolean, server_default=text("false"))
