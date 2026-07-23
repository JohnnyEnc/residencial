from fastapi import APIRouter, HTTPException, status
from sqlalchemy.orm import joinedload

from app.api.v1.auth import serialize_user
from app.core.deps import AdminUser, CurrentUser, DbSession
from app.models.unit import UnitMember
from app.models.user import User, UserRole
from app.schemas.user import ProfileUpdate, ResidentContactOut, UserOut

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("/residents", response_model=list[ResidentContactOut])
def list_resident_contacts(db: DbSession, user: CurrentUser):
    """Directorio de contactos de residentes (teléfonos del condominio)."""
    q = (
        db.query(User)
        .options(joinedload(User.memberships).joinedload(UnitMember.unit))
        .filter(User.role == UserRole.resident, User.active.is_(True))
        .order_by(User.name)
    )
    if user.role != UserRole.admin:
        q = q.filter(User.show_in_directory.is_(True))

    results: list[ResidentContactOut] = []
    for u in q.all():
        results.append(
            ResidentContactOut(
                id=u.id,
                name=u.name,
                phone=u.phone,
                phone_secondary=u.phone_secondary,
                whatsapp=u.whatsapp,
                unit_codes=[m.unit.code for m in u.memberships if m.unit],
                show_in_directory=bool(u.show_in_directory),
            )
        )
    return results


@router.patch("/me", response_model=UserOut)
def update_my_contact(payload: ProfileUpdate, db: DbSession, user: CurrentUser):
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(user, key, value)
    db.add(user)
    db.commit()
    user = (
        db.query(User)
        .options(joinedload(User.memberships).joinedload(UnitMember.unit))
        .filter(User.id == user.id)
        .one()
    )
    return serialize_user(user)


@router.patch("/residents/{user_id}", response_model=UserOut)
def admin_update_resident_contact(user_id: int, payload: ProfileUpdate, db: DbSession, _: AdminUser):
    target = (
        db.query(User)
        .options(joinedload(User.memberships).joinedload(UnitMember.unit))
        .filter(User.id == user_id, User.role == UserRole.resident)
        .first()
    )
    if not target:
        raise HTTPException(status_code=404, detail="Residente no encontrado")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(target, key, value)
    db.add(target)
    db.commit()
    target = (
        db.query(User)
        .options(joinedload(User.memberships).joinedload(UnitMember.unit))
        .filter(User.id == user_id)
        .one()
    )
    return serialize_user(target)
