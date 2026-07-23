from fastapi import APIRouter, HTTPException, status

from app.core.deps import AdminUser, CurrentUser, DbSession
from app.models.service import ServiceCategory, ServiceProvider
from app.schemas.service import ServiceProviderCreate, ServiceProviderOut, ServiceProviderUpdate

router = APIRouter(prefix="/services", tags=["services"])

CATEGORY_LABELS = {
    ServiceCategory.plomeria: "Plomería",
    ServiceCategory.electricidad: "Electricidad",
    ServiceCategory.mecanica: "Mecánica",
    ServiceCategory.cerrajeria: "Cerrajería",
    ServiceCategory.aires: "Aires acondicionados",
    ServiceCategory.limpieza: "Limpieza",
    ServiceCategory.pintura: "Pintura",
    ServiceCategory.jardineria: "Jardinería",
    ServiceCategory.construccion: "Construcción / albañilería",
    ServiceCategory.otro: "Otro",
}


@router.get("/categories")
def list_categories(_: CurrentUser):
    return [{"value": c.value, "label": CATEGORY_LABELS[c]} for c in ServiceCategory]


@router.get("", response_model=list[ServiceProviderOut])
def list_services(
    db: DbSession,
    user: CurrentUser,
    category: ServiceCategory | None = None,
    q: str | None = None,
    include_inactive: bool = False,
):
    query = db.query(ServiceProvider)
    if user.role.value != "admin" or not include_inactive:
        query = query.filter(ServiceProvider.active.is_(True))
    if category:
        query = query.filter(ServiceProvider.category == category)
    if q:
        like = f"%{q.strip()}%"
        query = query.filter(
            (ServiceProvider.name.ilike(like)) | (ServiceProvider.description.ilike(like))
        )
    return query.order_by(ServiceProvider.category, ServiceProvider.name).all()


@router.post("", response_model=ServiceProviderOut, status_code=status.HTTP_201_CREATED)
def create_service(payload: ServiceProviderCreate, db: DbSession, admin: AdminUser):
    provider = ServiceProvider(**payload.model_dump(), created_by=admin.id)
    db.add(provider)
    db.commit()
    db.refresh(provider)
    return provider


@router.patch("/{provider_id}", response_model=ServiceProviderOut)
def update_service(provider_id: int, payload: ServiceProviderUpdate, db: DbSession, _: AdminUser):
    provider = db.get(ServiceProvider, provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(provider, key, value)
    db.add(provider)
    db.commit()
    db.refresh(provider)
    return provider


@router.delete("/{provider_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_service(provider_id: int, db: DbSession, _: AdminUser):
    provider = db.get(ServiceProvider, provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    db.delete(provider)
    db.commit()
