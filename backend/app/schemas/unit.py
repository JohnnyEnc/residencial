from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.unit import MemberRelation, UnitStatus


class UnitCreate(BaseModel):
    code: str = Field(min_length=1, max_length=40)
    block: str | None = None
    number: str
    floor: str | None = None
    status: UnitStatus = UnitStatus.active


class UnitUpdate(BaseModel):
    code: str | None = None
    block: str | None = None
    number: str | None = None
    floor: str | None = None
    status: UnitStatus | None = None


class MemberOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    user_name: str
    user_email: str
    relation: MemberRelation


class UnitOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    block: str | None
    number: str
    floor: str | None
    status: UnitStatus
    created_at: datetime
    members: list[MemberOut] = []
