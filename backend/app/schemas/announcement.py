from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.announcement import AnnouncementPriority


class AnnouncementCreate(BaseModel):
    title: str = Field(max_length=200)
    body: str
    priority: AnnouncementPriority = AnnouncementPriority.normal
    expires_at: datetime | None = None


class AnnouncementOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    body: str
    priority: AnnouncementPriority
    published_at: datetime
    expires_at: datetime | None
    created_by: int
    read: bool = False
