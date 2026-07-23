from fastapi import APIRouter, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.core.deps import AdminUser, CurrentUser, DbSession
from app.core.security import get_password_hash
from app.models.unit import Unit, UnitMember
from app.models.user import User, UserRole
from app.api.v1.auth import serialize_user
from app.schemas.user import UserCreate, UserOut, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserOut])
def list_users(db: DbSession, _: AdminUser, role: UserRole | None = None):
    q = db.query(User).options(joinedload(User.memberships).joinedload(UnitMember.unit))
    if role:
        q = q.filter(User.role == role)
    return [serialize_user(u) for u in q.order_by(User.name).all()]


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: DbSession, _: AdminUser):
    if db.query(User).filter(User.email == payload.email.lower()).first():
        raise HTTPException(status_code=400, detail="Email ya registrado")
    user = User(
        email=payload.email.lower(),
        password_hash=get_password_hash(payload.password),
        name=payload.name,
        phone=payload.phone,
        phone_secondary=payload.phone_secondary,
        whatsapp=payload.whatsapp,
        show_in_directory=payload.show_in_directory,
        role=payload.role,
        active=payload.active,
    )
    db.add(user)
    db.flush()
    for unit_id in payload.unit_ids:
        unit = db.get(Unit, unit_id)
        if not unit:
            raise HTTPException(status_code=400, detail=f"Vivienda {unit_id} no existe")
        db.add(UnitMember(user_id=user.id, unit_id=unit_id, relation=payload.relation))
    db.commit()
    db.refresh(user)
    user = (
        db.query(User)
        .options(joinedload(User.memberships).joinedload(UnitMember.unit))
        .filter(User.id == user.id)
        .one()
    )
    return serialize_user(user)


@router.patch("/{user_id}", response_model=UserOut)
def update_user(user_id: int, payload: UserUpdate, db: DbSession, _: AdminUser):
    user = (
        db.query(User)
        .options(joinedload(User.memberships).joinedload(UnitMember.unit))
        .filter(User.id == user_id)
        .first()
    )
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    data = payload.model_dump(exclude_unset=True)
    unit_ids = data.pop("unit_ids", None)
    relation = data.pop("relation", None)
    password = data.pop("password", None)
    for k, v in data.items():
        setattr(user, k, v)
    if password:
        user.password_hash = get_password_hash(password)
    if unit_ids is not None:
        db.query(UnitMember).filter(UnitMember.user_id == user.id).delete()
        from app.models.unit import MemberRelation

        rel = relation or MemberRelation.owner
        for unit_id in unit_ids:
            if not db.get(Unit, unit_id):
                raise HTTPException(status_code=400, detail=f"Vivienda {unit_id} no existe")
            db.add(UnitMember(user_id=user.id, unit_id=unit_id, relation=rel))
    db.commit()
    user = (
        db.query(User)
        .options(joinedload(User.memberships).joinedload(UnitMember.unit))
        .filter(User.id == user_id)
        .one()
    )
    return serialize_user(user)


@router.get("/me/summary")
def my_summary(user: CurrentUser, db: DbSession):
    from app.models.payment import ChargeStatus, UnitCharge

    unit_ids = [m.unit_id for m in user.memberships]
    pending = 0
    paid = 0
    if unit_ids:
        charges = db.query(UnitCharge).filter(UnitCharge.unit_id.in_(unit_ids)).all()
        pending = sum(1 for c in charges if c.status in (ChargeStatus.pending, ChargeStatus.overdue, ChargeStatus.submitted))
        paid = sum(1 for c in charges if c.status == ChargeStatus.paid)
    return {"pending_charges": pending, "paid_charges": paid, "units": len(unit_ids)}
