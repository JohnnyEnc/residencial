from decimal import Decimal

from pydantic import BaseModel


class StatusCount(BaseModel):
    status: str
    count: int
    amount: Decimal = Decimal("0")


class UnitPaymentRow(BaseModel):
    unit_id: int
    unit_code: str
    amount: Decimal
    status: str
    resident_name: str | None = None


class MonthlyCollection(BaseModel):
    year: int
    month: int
    label: str
    paid: Decimal
    pending: Decimal
    overdue: Decimal
    submitted: Decimal


class ReportStatusCount(BaseModel):
    status: str
    count: int


class DashboardStats(BaseModel):
    total_units: int
    total_residents: int
    total_staff: int
    open_reports: int
    collection_rate: float
    paid_amount: Decimal
    pending_amount: Decimal
    overdue_amount: Decimal
    submitted_amount: Decimal
    charges_by_status: list[StatusCount]
    paid_units: list[UnitPaymentRow]
    unpaid_units: list[UnitPaymentRow]
    monthly_collection: list[MonthlyCollection]
    reports_by_status: list[ReportStatusCount]
    pending_payment_reviews: int
