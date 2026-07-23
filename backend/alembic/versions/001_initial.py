"""Initial schema

Revision ID: 001_initial
Revises:
Create Date: 2026-07-23
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("phone", sa.String(40), nullable=True),
        sa.Column("role", sa.Enum("admin", "resident", "staff", name="user_role"), nullable=False),
        sa.Column("active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_role", "users", ["role"])

    op.create_table(
        "units",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(40), nullable=False),
        sa.Column("block", sa.String(40), nullable=True),
        sa.Column("number", sa.String(40), nullable=False),
        sa.Column("floor", sa.String(20), nullable=True),
        sa.Column("status", sa.Enum("active", "inactive", name="unit_status"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_units_code", "units", ["code"], unique=True)

    op.create_table(
        "unit_members",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("unit_id", sa.Integer(), sa.ForeignKey("units.id", ondelete="CASCADE"), nullable=False),
        sa.Column("relation", sa.Enum("owner", "tenant", name="member_relation"), nullable=False),
        sa.UniqueConstraint("user_id", "unit_id", name="uq_user_unit"),
    )

    op.create_table(
        "fee_periods",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("month", sa.Integer(), nullable=False),
        sa.Column("amount_default", sa.Numeric(12, 2), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column("label", sa.String(120), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("year", "month", name="uq_fee_year_month"),
    )

    op.create_table(
        "unit_charges",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("unit_id", sa.Integer(), sa.ForeignKey("units.id", ondelete="CASCADE"), nullable=False),
        sa.Column("period_id", sa.Integer(), sa.ForeignKey("fee_periods.id", ondelete="CASCADE"), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column(
            "status",
            sa.Enum("pending", "submitted", "paid", "overdue", name="charge_status"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("unit_id", "period_id", name="uq_unit_period"),
    )
    op.create_index("ix_unit_charges_unit_id", "unit_charges", ["unit_id"])
    op.create_index("ix_unit_charges_period_id", "unit_charges", ["period_id"])
    op.create_index("ix_unit_charges_status", "unit_charges", ["status"])

    op.create_table(
        "payments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("charge_id", sa.Integer(), sa.ForeignKey("unit_charges.id", ondelete="CASCADE"), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("method", sa.String(60), nullable=True),
        sa.Column("proof_url", sa.String(500), nullable=True),
        sa.Column("submitted_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("submitted_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("reviewed_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "status",
            sa.Enum("submitted", "approved", "rejected", name="payment_status"),
            nullable=False,
        ),
        sa.Column("note", sa.String(500), nullable=True),
    )
    op.create_index("ix_payments_charge_id", "payments", ["charge_id"])
    op.create_index("ix_payments_status", "payments", ["status"])

    op.create_table(
        "reports",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("unit_id", sa.Integer(), sa.ForeignKey("units.id"), nullable=True),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("assigned_to", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("category", sa.String(80), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("location", sa.String(200), nullable=True),
        sa.Column("photo_url", sa.String(500), nullable=True),
        sa.Column(
            "status",
            sa.Enum("open", "assigned", "in_progress", "resolved", "closed", name="report_status"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    op.create_table(
        "report_updates",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("report_id", sa.Integer(), sa.ForeignKey("reports.id", ondelete="CASCADE"), nullable=False),
        sa.Column("author_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("note", sa.Text(), nullable=False),
        sa.Column(
            "status_to",
            sa.Enum(
                "open",
                "assigned",
                "in_progress",
                "resolved",
                "closed",
                name="report_update_status",
            ),
            nullable=True,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    op.create_table(
        "announcements",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column(
            "priority",
            sa.Enum("low", "normal", "high", name="announcement_priority"),
            nullable=False,
        ),
        sa.Column("published_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
    )

    op.create_table(
        "announcement_reads",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "announcement_id",
            sa.Integer(),
            sa.ForeignKey("announcements.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("read_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("announcement_id", "user_id", name="uq_announcement_user"),
    )


def downgrade() -> None:
    op.drop_table("announcement_reads")
    op.drop_table("announcements")
    op.drop_table("report_updates")
    op.drop_table("reports")
    op.drop_table("payments")
    op.drop_table("unit_charges")
    op.drop_table("fee_periods")
    op.drop_table("unit_members")
    op.drop_table("units")
    op.drop_table("users")
    for name in [
        "user_role",
        "unit_status",
        "member_relation",
        "charge_status",
        "payment_status",
        "report_status",
        "report_update_status",
        "announcement_priority",
    ]:
        sa.Enum(name=name).drop(op.get_bind(), checkfirst=True)
