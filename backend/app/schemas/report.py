from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.report import ReportStatus


class ReportCreate(BaseModel):
    unit_id: int | None = None
    category: str
    title: str = Field(max_length=200)
    description: str
    location: str | None = None


class ReportAssign(BaseModel):
    assigned_to: int


class ReportUpdateCreate(BaseModel):
    note: str
    status_to: ReportStatus | None = None


class ReportUpdateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    report_id: int
    author_id: int
    note: str
    status_to: ReportStatus | None
    created_at: datetime


class ReportOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    unit_id: int | None
    unit_code: str | None = None
    created_by: int
    creator_name: str | None = None
    assigned_to: int | None
    assignee_name: str | None = None
    category: str
    title: str
    description: str
    location: str | None
    photo_url: str | None
    status: ReportStatus
    created_at: datetime
    updated_at: datetime
    updates: list[ReportUpdateOut] = []
