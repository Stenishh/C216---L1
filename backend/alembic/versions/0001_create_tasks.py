"""Cria a tabela de tarefas.

Revision ID: 0001
Revises: None
"""

import sqlalchemy as sa

from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(120), nullable=False),
        sa.Column("description", sa.String(1000), server_default="", nullable=False),
        sa.Column(
            "completed", sa.Boolean(), server_default=sa.text("false"), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
        sqlite_autoincrement=True,
    )


def downgrade():
    op.drop_table("tasks")
