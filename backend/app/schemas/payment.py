from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.payment import ChargeStatus, PaymentStatus


class FeePeriodCreate(BaseModel):
    year: int
    month: int = Field(ge=1, le=12)
    amount_default: Decimal
    due_date: date
    label: str | None = None


class FeePeriodOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    year: int
    month: int
    amount_default: Decimal
    due_date: date
    label: str | None
    created_at: datetime


class UnitChargeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    unit_id: int
    unit_code: str
    period_id: int
    period_label: str
    amount: Decimal
    status: ChargeStatus
    created_at: datetime


class PaymentCreate(BaseModel):
    charge_id: int
    amount: Decimal
    method: str | None = None
    note: str | None = None


class PaymentReview(BaseModel):
    status: PaymentStatus
    note: str | None = None


class PaymentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    charge_id: int
    amount: Decimal
    method: str | None
    proof_url: str | None
    submitted_by: int | None
    submitted_at: datetime
    reviewed_by: int | None
    reviewed_at: datetime | None
    status: PaymentStatus
    note: str | None
