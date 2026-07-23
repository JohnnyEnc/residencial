from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1 import api_router
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.user import User
from app.services.uploads import ensure_upload_dir

app = FastAPI(title="Residencial API", version="1.0.0")

cors_kwargs: dict = {
    "allow_methods": ["*"],
    "allow_headers": ["*"],
}
if settings.cors_origin_list == ["*"]:
    cors_kwargs["allow_origins"] = ["*"]
    cors_kwargs["allow_credentials"] = False
else:
    cors_kwargs["allow_origins"] = settings.cors_origin_list
    cors_kwargs["allow_credentials"] = True
    cors_kwargs["allow_origin_regex"] = r"https://.*\.onrender\.com"

app.add_middleware(CORSMiddleware, **cors_kwargs)

upload_path = ensure_upload_dir()
app.mount("/uploads", StaticFiles(directory=str(upload_path)), name="uploads")
app.include_router(api_router)

STATIC_DIR = Path(__file__).resolve().parents[1] / "static"
API_PREFIXES = ("api/", "docs", "redoc", "openapi.json", "health", "uploads/")


@app.get("/health")
def health():
    db_ok = False
    users = 0
    try:
        db = SessionLocal()
        try:
            users = db.query(User).count()
            db_ok = True
        finally:
            db.close()
    except Exception as exc:  # noqa: BLE001
        return {"status": "degraded", "database": False, "error": str(exc), "users": 0}
    return {"status": "ok", "database": db_ok, "users": users}


if STATIC_DIR.exists():
    assets_dir = STATIC_DIR / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    @app.get("/{full_path:path}")
    async def spa_fallback(full_path: str):
        # Nunca devolver el SPA para rutas de API/docs (evita HTML donde el front espera JSON).
        if full_path.startswith(API_PREFIXES) or full_path in {"docs", "redoc", "openapi.json", "health"}:
            raise HTTPException(status_code=404, detail="Not Found")

        candidate = STATIC_DIR / full_path
        if full_path and candidate.is_file():
            return FileResponse(candidate)
        index = STATIC_DIR / "index.html"
        if index.exists():
            return FileResponse(index)
        return {"detail": "Frontend no desplegado. Ejecuta el build de Vue."}
