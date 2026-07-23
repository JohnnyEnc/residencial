import enum
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import str_enum


class UnitStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"


class MemberRelation(str, enum.Enum):
    owner = "owner"
    tenant = "tenant"


class Unit(Base):
    __tablename__ = "units"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    block: Mapped[str | None] = mapped_column(String(40), nullable=True)
    number: Mapped[str] = mapped_column(String(40))
    floor: Mapped[str | None] = mapped_column(String(20), nullable=True)
    status: Mapped[UnitStatus] = mapped_column(str_enum(UnitStatus, "unit_status"), default=UnitStatus.active)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    members = relationship("UnitMember", back_populates="unit", cascade="all, delete-orphan")
    charges = relationship("UnitCharge", back_populates="unit")


class UnitMember(Base):
    __tablename__ = "unit_members"
    __table_args__ = (UniqueConstraint("user_id", "unit_id", name="uq_user_unit"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    unit_id: Mapped[int] = mapped_column(ForeignKey("units.id", ondelete="CASCADE"))
    relation: Mapped[MemberRelation] = mapped_column(str_enum(MemberRelation, "member_relation"))

    user = relationship("User", back_populates="memberships")
    unit = relationship("Unit", back_populates="members")
