from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
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

# Health primero y simple: Render usa esto para marcar el servicio como vivo.
@app.get("/health")
def health():
    payload: dict = {"status": "ok"}
    try:
        db = SessionLocal()
        try:
            payload["database"] = True
            payload["users"] = db.query(User).count()
        finally:
            db.close()
    except Exception as exc:  # noqa: BLE001
        payload["database"] = False
        payload["users"] = 0
        payload["error"] = str(exc)
    return payload


upload_path = ensure_upload_dir()
app.mount("/uploads", StaticFiles(directory=str(upload_path)), name="uploads")
app.include_router(api_router)

STATIC_DIR = Path(__file__).resolve().parents[1] / "static"


def _is_api_path(path: str) -> bool:
    return (
        path.startswith("/api")
        or path.startswith("/uploads")
        or path.startswith("/assets")
        or path in {"/health", "/docs", "/redoc", "/openapi.json"}
        or path.startswith("/docs/")
        or path.startswith("/redoc/")
    )


if STATIC_DIR.exists():
    assets_dir = STATIC_DIR / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    @app.get("/")
    async def spa_root():
        return FileResponse(STATIC_DIR / "index.html")

    @app.exception_handler(404)
    async def not_found_handler(request: Request, _exc: Exception):
        """SPA fallback sin shadowing de /health ni /api (evita que Render tumbe el servicio)."""
        path = request.url.path
        if _is_api_path(path) or request.method != "GET":
            detail = getattr(_exc, "detail", "Not Found")
            return JSONResponse({"detail": detail}, status_code=404)

        # Archivos estáticos en la raíz del build (vite.svg, favicon, etc.)
        candidate = STATIC_DIR / path.lstrip("/")
        if path != "/" and candidate.is_file():
            return FileResponse(candidate)

        index = STATIC_DIR / "index.html"
        if index.exists():
            return FileResponse(index)
        return JSONResponse({"detail": "Frontend no desplegado"}, status_code=404)
else:

    @app.get("/")
    def root_without_frontend():
        return {"detail": "Frontend no desplegado. Revisa el build Docker."}
