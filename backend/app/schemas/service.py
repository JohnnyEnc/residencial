from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.service import ServiceCategory


class ServiceProviderCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    category: ServiceCategory
    phone: str = Field(min_length=5, max_length=40)
    phone_alt: str | None = None
    whatsapp: str | None = None
    description: str | None = None
    active: bool = True


class ServiceProviderUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    category: ServiceCategory | None = None
    phone: str | None = None
    phone_alt: str | None = None
    whatsapp: str | None = None
    description: str | None = None
    active: bool | None = None


class ServiceProviderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category: ServiceCategory
    phone: str
    phone_alt: str | None
    whatsapp: str | None
    description: str | None
    active: bool
    created_by: int | None
    created_at: datetime
