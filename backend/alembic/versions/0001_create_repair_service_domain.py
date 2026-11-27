"""Cria clientes, ordens de servico e eventos do atendimento.

Revision ID: 0001
Revises:
"""

import sqlalchemy as sa

from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "customers",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=False), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("phone", sa.String(length=11), nullable=False),
        sa.Column("email", sa.String(length=254), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "length(phone) IN (10, 11) AND translate(phone, '0123456789', '') = ''",
            name=op.f("ck_customers_phone_digits"),
        ),
        sa.CheckConstraint(
            "length(trim(name)) BETWEEN 1 AND 100",
            name=op.f("ck_customers_name_length"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_customers")),
    )
    op.create_table(
        "service_orders",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=False), nullable=False),
        sa.Column("customer_id", sa.BigInteger(), nullable=False),
        sa.Column(
            "equipment_type",
            sa.Enum(
                "computer",
                "notebook",
                name="equipment_type",
                native_enum=False,
                create_constraint=True,
            ),
            nullable=False,
        ),
        sa.Column("brand", sa.String(length=100), nullable=False),
        sa.Column("model", sa.String(length=100), nullable=False),
        sa.Column("serial_number", sa.String(length=100), nullable=True),
        sa.Column("reported_problem", sa.String(length=2000), nullable=False),
        sa.Column("diagnosis", sa.String(length=2000), nullable=True),
        sa.Column("budget_amount", sa.Numeric(precision=8, scale=2), nullable=True),
        sa.Column(
            "budget_decision",
            sa.Enum(
                "not_requested",
                "pending",
                "approved",
                "rejected",
                name="budget_decision",
                native_enum=False,
                create_constraint=True,
            ),
            server_default="not_requested",
            nullable=False,
        ),
        sa.Column("service_performed", sa.String(length=2000), nullable=True),
        sa.Column("cancellation_reason", sa.String(length=500), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "received",
                "in_diagnosis",
                "awaiting_approval",
                "in_repair",
                "completed",
                "delivered",
                "cancelled",
                name="order_status",
                native_enum=False,
                create_constraint=True,
            ),
            server_default="received",
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "budget_amount IS NULL OR budget_amount BETWEEN 0 AND 999999.99",
            name=op.f("ck_service_orders_budget_range"),
        ),
        sa.CheckConstraint(
            "cancellation_reason IS NULL OR length(trim(cancellation_reason)) BETWEEN 1 AND 500",
            name=op.f("ck_service_orders_cancellation_reason_length"),
        ),
        sa.CheckConstraint(
            "length(trim(brand)) BETWEEN 1 AND 100",
            name=op.f("ck_service_orders_brand_length"),
        ),
        sa.CheckConstraint(
            "length(trim(model)) BETWEEN 1 AND 100",
            name=op.f("ck_service_orders_model_length"),
        ),
        sa.CheckConstraint(
            "length(trim(reported_problem)) BETWEEN 1 AND 2000",
            name=op.f("ck_service_orders_reported_problem_length"),
        ),
        sa.ForeignKeyConstraint(
            ["customer_id"],
            ["customers.id"],
            name=op.f("fk_service_orders_customer_id_customers"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_service_orders")),
    )
    op.create_index(
        op.f("ix_service_orders_customer_id"),
        "service_orders",
        ["customer_id"],
        unique=False,
    )
    op.create_index(
        "ix_service_orders_status_created_at",
        "service_orders",
        ["status", "created_at"],
        unique=False,
    )
    op.create_table(
        "order_events",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=False), nullable=False),
        sa.Column("order_id", sa.BigInteger(), nullable=False),
        sa.Column(
            "action",
            sa.Enum(
                "open",
                "begin_diagnosis",
                "request_approval",
                "approve_budget",
                "reject_budget",
                "start_repair",
                "complete_repair",
                "deliver",
                "cancel",
                name="event_action",
                native_enum=False,
                create_constraint=True,
            ),
            nullable=False,
        ),
        sa.Column(
            "previous_status",
            sa.Enum(
                "received",
                "in_diagnosis",
                "awaiting_approval",
                "in_repair",
                "completed",
                "delivered",
                "cancelled",
                name="previous_status",
                native_enum=False,
                create_constraint=True,
            ),
            nullable=True,
        ),
        sa.Column(
            "resulting_status",
            sa.Enum(
                "received",
                "in_diagnosis",
                "awaiting_approval",
                "in_repair",
                "completed",
                "delivered",
                "cancelled",
                name="resulting_status",
                native_enum=False,
                create_constraint=True,
            ),
            nullable=False,
        ),
        sa.Column("observation", sa.String(length=2000), nullable=True),
        sa.Column("approved_amount", sa.Numeric(precision=8, scale=2), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "approved_amount IS NULL OR approved_amount BETWEEN 0 AND 999999.99",
            name=op.f("ck_order_events_approved_amount_range"),
        ),
        sa.ForeignKeyConstraint(
            ["order_id"],
            ["service_orders.id"],
            name=op.f("fk_order_events_order_id_service_orders"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_order_events")),
    )
    op.create_index(
        op.f("ix_order_events_order_id"), "order_events", ["order_id"], unique=False
    )


def downgrade():
    op.drop_index(op.f("ix_order_events_order_id"), table_name="order_events")
    op.drop_table("order_events")
    op.drop_index("ix_service_orders_status_created_at", table_name="service_orders")
    op.drop_index(op.f("ix_service_orders_customer_id"), table_name="service_orders")
    op.drop_table("service_orders")
    op.drop_table("customers")
