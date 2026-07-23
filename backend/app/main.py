from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1 import api_router
from app.core.config import settings
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


@app.get("/health")
def health():
    return {"status": "ok"}


if STATIC_DIR.exists():
    assets_dir = STATIC_DIR / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    @app.get("/{full_path:path}")
    async def spa_fallback(full_path: str):
        # No interceptar rutas de API ya registradas; este catch-all es el último.
        candidate = STATIC_DIR / full_path
        if full_path and candidate.is_file():
            return FileResponse(candidate)
        index = STATIC_DIR / "index.html"
        if index.exists():
            return FileResponse(index)
        return {"detail": "Frontend no desplegado. Ejecuta el build de Vue."}
