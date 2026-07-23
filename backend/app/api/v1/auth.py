from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import CurrentUser
from app.core.security import create_access_token, verify_password
from app.models.unit import Unit
from app.models.user import User
from app.schemas.user import LoginRequest, TokenOut, UnitBrief, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


def serialize_user(user: User) -> UserOut:
    units = []
    for m in user.memberships:
        units.append(
            UnitBrief(
                id=m.unit.id,
                code=m.unit.code,
                block=m.unit.block,
                number=m.unit.number,
            )
        )
    return UserOut(
        id=user.id,
        email=user.email,
        name=user.name,
        phone=user.phone,
        role=user.role,
        active=user.active,
        created_at=user.created_at,
        units=units,
    )


@router.post("/login", response_model=TokenOut)
def login_json(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")
    if not user.active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario inactivo")
    token = create_access_token(user.id, {"role": user.role.value})
    return TokenOut(access_token=token)


@router.post("/token", response_model=TokenOut)
def login_form(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form.username.lower()).first()
    if not user or not verify_password(form.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")
    token = create_access_token(user.id, {"role": user.role.value})
    return TokenOut(access_token=token)


@router.get("/me", response_model=UserOut)
def me(user: CurrentUser):
    return serialize_user(user)
