from datetime import date, datetime, timezone
from decimal import Decimal

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from sqlalchemy.orm import joinedload

from app.core.deps import AdminUser, CurrentUser, DbSession
from app.models.payment import ChargeStatus, FeePeriod, Payment, PaymentStatus, UnitCharge
from app.models.unit import Unit, UnitStatus
from app.models.user import UserRole
from app.schemas.payment import (
    FeePeriodCreate,
    FeePeriodOut,
    PaymentCreate,
    PaymentOut,
    PaymentReview,
    UnitChargeOut,
)
from app.services.uploads import save_upload

router = APIRouter(tags=["payments"])


def period_label(p: FeePeriod) -> str:
    return p.label or f"{p.month:02d}/{p.year}"


def serialize_charge(c: UnitCharge) -> UnitChargeOut:
    return UnitChargeOut(
        id=c.id,
        unit_id=c.unit_id,
        unit_code=c.unit.code if c.unit else str(c.unit_id),
        period_id=c.period_id,
        period_label=period_label(c.period) if c.period else str(c.period_id),
        amount=c.amount,
        status=c.status,
        created_at=c.created_at,
    )


@router.get("/fee-periods", response_model=list[FeePeriodOut])
def list_periods(db: DbSession, _: CurrentUser):
    return db.query(FeePeriod).order_by(FeePeriod.year.desc(), FeePeriod.month.desc()).all()


@router.post("/fee-periods", response_model=FeePeriodOut, status_code=status.HTTP_201_CREATED)
def create_period(payload: FeePeriodCreate, db: DbSession, _: AdminUser):
    exists = (
        db.query(FeePeriod)
        .filter(FeePeriod.year == payload.year, FeePeriod.month == payload.month)
        .first()
    )
    if exists:
        raise HTTPException(status_code=400, detail="Ya existe un periodo para ese mes")
    period = FeePeriod(**payload.model_dump())
    db.add(period)
    db.commit()
    db.refresh(period)
    return period


@router.post("/fee-periods/{period_id}/generate-charges", response_model=list[UnitChargeOut])
def generate_charges(period_id: int, db: DbSession, _: AdminUser):
    period = db.get(FeePeriod, period_id)
    if not period:
        raise HTTPException(status_code=404, detail="Periodo no encontrado")
    units = db.query(Unit).filter(Unit.status == UnitStatus.active).all()
    created: list[UnitCharge] = []
    today = date.today()
    status_value = ChargeStatus.overdue if period.due_date < today else ChargeStatus.pending
    for unit in units:
        existing = (
            db.query(UnitCharge)
            .filter(UnitCharge.unit_id == unit.id, UnitCharge.period_id == period.id)
            .first()
        )
        if existing:
            continue
        charge = UnitCharge(
            unit_id=unit.id,
            period_id=period.id,
            amount=period.amount_default,
            status=status_value,
        )
        db.add(charge)
        created.append(charge)
    db.commit()
    charges = (
        db.query(UnitCharge)
        .options(joinedload(UnitCharge.unit), joinedload(UnitCharge.period))
        .filter(UnitCharge.period_id == period_id)
        .all()
    )
    return [serialize_charge(c) for c in charges]


@router.get("/charges", response_model=list[UnitChargeOut])
def list_charges(
    db: DbSession,
    user: CurrentUser,
    period_id: int | None = None,
    status_filter: ChargeStatus | None = None,
):
    q = db.query(UnitCharge).options(joinedload(UnitCharge.unit), joinedload(UnitCharge.period))
    if user.role == UserRole.resident:
        unit_ids = [m.unit_id for m in user.memberships]
        q = q.filter(UnitCharge.unit_id.in_(unit_ids or [-1]))
    if period_id:
        q = q.filter(UnitCharge.period_id == period_id)
    if status_filter:
        q = q.filter(UnitCharge.status == status_filter)
    return [serialize_charge(c) for c in q.order_by(UnitCharge.id.desc()).all()]


@router.get("/payments", response_model=list[PaymentOut])
def list_payments(db: DbSession, user: CurrentUser, status_filter: PaymentStatus | None = None):
    q = db.query(Payment).options(joinedload(Payment.charge).joinedload(UnitCharge.unit))
    if user.role == UserRole.resident:
        unit_ids = [m.unit_id for m in user.memberships]
        q = q.join(UnitCharge).filter(UnitCharge.unit_id.in_(unit_ids or [-1]))
    if status_filter:
        q = q.filter(Payment.status == status_filter)
    return q.order_by(Payment.submitted_at.desc()).all()


@router.post("/payments", response_model=PaymentOut, status_code=status.HTTP_201_CREATED)
async def submit_payment(
    db: DbSession,
    user: CurrentUser,
    charge_id: int,
    amount: Decimal,
    method: str | None = None,
    note: str | None = None,
    proof: UploadFile | None = File(None),
):
    charge = (
        db.query(UnitCharge)
        .options(joinedload(UnitCharge.unit))
        .filter(UnitCharge.id == charge_id)
        .first()
    )
    if not charge:
        raise HTTPException(status_code=404, detail="Cargo no encontrado")
    if user.role == UserRole.resident:
        unit_ids = [m.unit_id for m in user.memberships]
        if charge.unit_id not in unit_ids:
            raise HTTPException(status_code=403, detail="Sin permiso")
    if charge.status == ChargeStatus.paid:
        raise HTTPException(status_code=400, detail="Este cargo ya está pagado")

    proof_url = None
    if proof and proof.filename:
        proof_url = await save_upload(proof, "proofs")

    payment = Payment(
        charge_id=charge.id,
        amount=amount,
        method=method,
        proof_url=proof_url,
        submitted_by=user.id,
        status=PaymentStatus.submitted,
        note=note,
    )
    charge.status = ChargeStatus.submitted
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment


@router.post("/payments/json", response_model=PaymentOut, status_code=status.HTTP_201_CREATED)
def submit_payment_json(payload: PaymentCreate, db: DbSession, user: CurrentUser):
    charge = db.get(UnitCharge, payload.charge_id)
    if not charge:
        raise HTTPException(status_code=404, detail="Cargo no encontrado")
    if user.role == UserRole.resident:
        unit_ids = [m.unit_id for m in user.memberships]
        if charge.unit_id not in unit_ids:
            raise HTTPException(status_code=403, detail="Sin permiso")
    if charge.status == ChargeStatus.paid:
        raise HTTPException(status_code=400, detail="Este cargo ya está pagado")
    payment = Payment(
        charge_id=charge.id,
        amount=payload.amount,
        method=payload.method,
        submitted_by=user.id,
        status=PaymentStatus.submitted,
        note=payload.note,
    )
    charge.status = ChargeStatus.submitted
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment


@router.patch("/payments/{payment_id}/review", response_model=PaymentOut)
def review_payment(payment_id: int, payload: PaymentReview, db: DbSession, admin: AdminUser):
    payment = db.get(Payment, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Pago no encontrado")
    if payload.status not in (PaymentStatus.approved, PaymentStatus.rejected):
        raise HTTPException(status_code=400, detail="Estado de revisión inválido")
    payment.status = payload.status
    payment.note = payload.note or payment.note
    payment.reviewed_by = admin.id
    payment.reviewed_at = datetime.now(timezone.utc)
    charge = db.get(UnitCharge, payment.charge_id)
    if charge:
        if payload.status == PaymentStatus.approved:
            charge.status = ChargeStatus.paid
        else:
            charge.status = ChargeStatus.pending
    db.commit()
    db.refresh(payment)
    return payment
