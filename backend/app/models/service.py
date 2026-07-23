import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.enums import str_enum


class ServiceCategory(str, enum.Enum):
    plomeria = "plomeria"
    electricidad = "electricidad"
    mecanica = "mecanica"
    cerrajeria = "cerrajeria"
    aires = "aires"
    limpieza = "limpieza"
    pintura = "pintura"
    jardineria = "jardineria"
    construccion = "construccion"
    otro = "otro"


class ServiceProvider(Base):
    """Directorio de proveedores de mantenimiento / oficios para residentes."""

    __tablename__ = "service_providers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    category: Mapped[ServiceCategory] = mapped_column(str_enum(ServiceCategory, "service_category"), index=True)
    phone: Mapped[str] = mapped_column(String(40))
    phone_alt: Mapped[str | None] = mapped_column(String(40), nullable=True)
    whatsapp: Mapped[str | None] = mapped_column(String(40), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
