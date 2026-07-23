from decimal import Decimal

from fastapi import APIRouter
from sqlalchemy import func

from app.core.deps import AdminUser, DbSession
from app.models.payment import ChargeStatus, FeePeriod, Payment, PaymentStatus, UnitCharge
from app.models.report import Report, ReportStatus
from app.models.unit import Unit, UnitMember
from app.models.user import User, UserRole
from app.schemas.dashboard import (
    DashboardStats,
    MonthlyCollection,
    ReportStatusCount,
    StatusCount,
    UnitPaymentRow,
)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStats)
def dashboard_stats(db: DbSession, _: AdminUser, period_id: int | None = None):
    total_units = db.query(Unit).count()
    total_residents = db.query(User).filter(User.role == UserRole.resident, User.active.is_(True)).count()
    total_staff = db.query(User).filter(User.role == UserRole.staff, User.active.is_(True)).count()
    open_reports = (
        db.query(Report)
        .filter(Report.status.in_([ReportStatus.open, ReportStatus.assigned, ReportStatus.in_progress]))
        .count()
    )
    pending_payment_reviews = (
        db.query(Payment).filter(Payment.status == PaymentStatus.submitted).count()
    )

    charge_q = db.query(UnitCharge).join(Unit).outerjoin(FeePeriod)
    if period_id:
        charge_q = charge_q.filter(UnitCharge.period_id == period_id)
    else:
        latest = db.query(FeePeriod).order_by(FeePeriod.year.desc(), FeePeriod.month.desc()).first()
        if latest:
            charge_q = charge_q.filter(UnitCharge.period_id == latest.id)
            period_id = latest.id

    charges = charge_q.all()

    amounts = {
        ChargeStatus.paid: Decimal("0"),
        ChargeStatus.pending: Decimal("0"),
        ChargeStatus.overdue: Decimal("0"),
        ChargeStatus.submitted: Decimal("0"),
    }
    counts = {s: 0 for s in ChargeStatus}
    for c in charges:
        amounts[c.status] += c.amount
        counts[c.status] += 1

    paid_amount = amounts[ChargeStatus.paid]
    pending_amount = amounts[ChargeStatus.pending]
    overdue_amount = amounts[ChargeStatus.overdue]
    submitted_amount = amounts[ChargeStatus.submitted]
    total_amount = paid_amount + pending_amount + overdue_amount + submitted_amount
    collection_rate = float((paid_amount / total_amount) * 100) if total_amount else 0.0

    charges_by_status = [
        StatusCount(status=s.value, count=counts[s], amount=amounts[s]) for s in ChargeStatus
    ]

    # Resident name per unit (first owner/tenant)
    members = (
        db.query(UnitMember, User)
        .join(User, User.id == UnitMember.user_id)
        .filter(User.role == UserRole.resident)
        .all()
    )
    unit_resident: dict[int, str] = {}
    for membership, user in members:
        unit_resident.setdefault(membership.unit_id, user.name)

    paid_units: list[UnitPaymentRow] = []
    unpaid_units: list[UnitPaymentRow] = []
    for c in charges:
        row = UnitPaymentRow(
            unit_id=c.unit_id,
            unit_code=c.unit.code if c.unit else str(c.unit_id),
            amount=c.amount,
            status=c.status.value,
            resident_name=unit_resident.get(c.unit_id),
        )
        if c.status == ChargeStatus.paid:
            paid_units.append(row)
        else:
            unpaid_units.append(row)

    periods = db.query(FeePeriod).order_by(FeePeriod.year.asc(), FeePeriod.month.asc()).limit(12).all()
    monthly: list[MonthlyCollection] = []
    for p in periods:
        p_charges = db.query(UnitCharge).filter(UnitCharge.period_id == p.id).all()
        bucket = {
            "paid": Decimal("0"),
            "pending": Decimal("0"),
            "overdue": Decimal("0"),
            "submitted": Decimal("0"),
        }
        for c in p_charges:
            bucket[c.status.value] += c.amount
        monthly.append(
            MonthlyCollection(
                year=p.year,
                month=p.month,
                label=p.label or f"{p.month:02d}/{p.year}",
                paid=bucket["paid"],
                pending=bucket["pending"],
                overdue=bucket["overdue"],
                submitted=bucket["submitted"],
            )
        )

    report_rows = (
        db.query(Report.status, func.count(Report.id)).group_by(Report.status).all()
    )
    reports_by_status = [ReportStatusCount(status=s.value, count=c) for s, c in report_rows]

    return DashboardStats(
        total_units=total_units,
        total_residents=total_residents,
        total_staff=total_staff,
        open_reports=open_reports,
        collection_rate=round(collection_rate, 1),
        paid_amount=paid_amount,
        pending_amount=pending_amount,
        overdue_amount=overdue_amount,
        submitted_amount=submitted_amount,
        charges_by_status=charges_by_status,
        paid_units=sorted(paid_units, key=lambda x: x.unit_code),
        unpaid_units=sorted(unpaid_units, key=lambda x: x.unit_code),
        monthly_collection=monthly,
        reports_by_status=reports_by_status,
        pending_payment_reviews=pending_payment_reviews,
    )
