from fastapi import APIRouter, HTTPException, status
from sqlalchemy.orm import joinedload

from app.core.deps import AdminUser, CurrentUser, DbSession
from app.models.unit import Unit, UnitMember
from app.models.user import User, UserRole
from app.schemas.unit import MemberOut, UnitCreate, UnitOut, UnitUpdate

router = APIRouter(prefix="/units", tags=["units"])


def serialize_unit(unit: Unit) -> UnitOut:
    members = [
        MemberOut(
            id=m.id,
            user_id=m.user_id,
            user_name=m.user.name,
            user_email=m.user.email,
            relation=m.relation,
        )
        for m in unit.members
    ]
    return UnitOut(
        id=unit.id,
        code=unit.code,
        block=unit.block,
        number=unit.number,
        floor=unit.floor,
        status=unit.status,
        created_at=unit.created_at,
        members=members,
    )


@router.get("", response_model=list[UnitOut])
def list_units(db: DbSession, user: CurrentUser):
    q = db.query(Unit).options(joinedload(Unit.members).joinedload(UnitMember.user))
    if user.role == UserRole.resident:
        unit_ids = [m.unit_id for m in user.memberships]
        q = q.filter(Unit.id.in_(unit_ids or [-1]))
    units = q.order_by(Unit.code).all()
    return [serialize_unit(u) for u in units]


@router.post("", response_model=UnitOut, status_code=status.HTTP_201_CREATED)
def create_unit(payload: UnitCreate, db: DbSession, _: AdminUser):
    if db.query(Unit).filter(Unit.code == payload.code).first():
        raise HTTPException(status_code=400, detail="Código de vivienda ya existe")
    unit = Unit(**payload.model_dump())
    db.add(unit)
    db.commit()
    db.refresh(unit)
    unit = (
        db.query(Unit)
        .options(joinedload(Unit.members).joinedload(UnitMember.user))
        .filter(Unit.id == unit.id)
        .one()
    )
    return serialize_unit(unit)


@router.get("/{unit_id}", response_model=UnitOut)
def get_unit(unit_id: int, db: DbSession, user: CurrentUser):
    unit = (
        db.query(Unit)
        .options(joinedload(Unit.members).joinedload(UnitMember.user))
        .filter(Unit.id == unit_id)
        .first()
    )
    if not unit:
        raise HTTPException(status_code=404, detail="Vivienda no encontrada")
    if user.role == UserRole.resident and unit_id not in [m.unit_id for m in user.memberships]:
        raise HTTPException(status_code=403, detail="Sin permiso")
    return serialize_unit(unit)


@router.patch("/{unit_id}", response_model=UnitOut)
def update_unit(unit_id: int, payload: UnitUpdate, db: DbSession, _: AdminUser):
    unit = db.get(Unit, unit_id)
    if not unit:
        raise HTTPException(status_code=404, detail="Vivienda no encontrada")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(unit, k, v)
    db.commit()
    unit = (
        db.query(Unit)
        .options(joinedload(Unit.members).joinedload(UnitMember.user))
        .filter(Unit.id == unit_id)
        .one()
    )
    return serialize_unit(unit)
