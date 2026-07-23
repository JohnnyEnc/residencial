from datetime import datetime

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
    phone_secondary: str | None = None
    whatsapp: str | None = None
    show_in_directory: bool = True
    role: UserRole
    active: bool = True


class UserCreate(UserBase):
    password: str = Field(min_length=6)
    unit_ids: list[int] = []
    relation: MemberRelation = MemberRelation.owner


class UserUpdate(BaseModel):
    name: str | None = None
    phone: str | None = None
    phone_secondary: str | None = None
    whatsapp: str | None = None
    show_in_directory: bool | None = None
    role: UserRole | None = None
    active: bool | None = None
    password: str | None = Field(default=None, min_length=6)
    unit_ids: list[int] | None = None
    relation: MemberRelation | None = None


class ProfileUpdate(BaseModel):
    """Actualización de contacto por el propio usuario."""

    phone: str | None = None
    phone_secondary: str | None = None
    whatsapp: str | None = None
    show_in_directory: bool | None = None


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
    phone_secondary: str | None = None
    whatsapp: str | None = None
    show_in_directory: bool = True
    role: UserRole
    active: bool
    created_at: datetime
    units: list[UnitBrief] = []


class ResidentContactOut(BaseModel):
    id: int
    name: str
    phone: str | None
    phone_secondary: str | None
    whatsapp: str | None
    unit_codes: list[str] = []
    show_in_directory: bool


class LoginRequest(BaseModel):
    email: str
    password: str
