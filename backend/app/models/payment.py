import enum
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import str_enum


class ChargeStatus(str, enum.Enum):
    pending = "pending"
    submitted = "submitted"
    paid = "paid"
    overdue = "overdue"


class PaymentStatus(str, enum.Enum):
    submitted = "submitted"
    approved = "approved"
    rejected = "rejected"


class FeePeriod(Base):
    __tablename__ = "fee_periods"
    __table_args__ = (UniqueConstraint("year", "month", name="uq_fee_year_month"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    year: Mapped[int]
    month: Mapped[int]
    amount_default: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    due_date: Mapped[date] = mapped_column(Date)
    label: Mapped[str | None] = mapped_column(String(120), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    charges = relationship("UnitCharge", back_populates="period")


class UnitCharge(Base):
    __tablename__ = "unit_charges"
    __table_args__ = (UniqueConstraint("unit_id", "period_id", name="uq_unit_period"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    unit_id: Mapped[int] = mapped_column(ForeignKey("units.id", ondelete="CASCADE"), index=True)
    period_id: Mapped[int] = mapped_column(ForeignKey("fee_periods.id", ondelete="CASCADE"), index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    status: Mapped[ChargeStatus] = mapped_column(
        str_enum(ChargeStatus, "charge_status"), default=ChargeStatus.pending, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    unit = relationship("Unit", back_populates="charges")
    period = relationship("FeePeriod", back_populates="charges")
    payments = relationship("Payment", back_populates="charge", cascade="all, delete-orphan")


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True)
    charge_id: Mapped[int] = mapped_column(ForeignKey("unit_charges.id", ondelete="CASCADE"), index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    method: Mapped[str | None] = mapped_column(String(60), nullable=True)
    proof_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    submitted_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    reviewed_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[PaymentStatus] = mapped_column(
        str_enum(PaymentStatus, "payment_status"), default=PaymentStatus.submitted, index=True
    )
    note: Mapped[str | None] = mapped_column(String(500), nullable=True)

    charge = relationship("UnitCharge", back_populates="payments")
