from fastapi import APIRouter

from app.api.v1 import announcements, auth, contacts, dashboard, payments, reports, services, units, users

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(units.router)
api_router.include_router(payments.router)
api_router.include_router(reports.router)
api_router.include_router(announcements.router)
api_router.include_router(dashboard.router)
api_router.include_router(contacts.router)
api_router.include_router(services.router)
