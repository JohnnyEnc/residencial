from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.unit import MemberRelation
from app.models.user import UserRole


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserBase(BaseModel):
    email: EmailStr
    name: str
    phone: str | None = None
    role: UserRole
    active: bool = True


class UserCreate(UserBase):
    password: str = Field(min_length=6)
    unit_ids: list[int] = []
    relation: MemberRelation = MemberRelation.owner


class UserUpdate(BaseModel):
    name: str | None = None
    phone: str | None = None
    role: UserRole | None = None
    active: bool | None = None
    password: str | None = Field(default=None, min_length=6)
    unit_ids: list[int] | None = None
    relation: MemberRelation | None = None


class UnitBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    block: str | None
    number: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    name: str
    phone: str | None
    role: UserRole
    active: bool
    created_at: datetime
    units: list[UnitBrief] = []


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
