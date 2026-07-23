from pathlib import Path
import uuid

from fastapi import UploadFile

from app.core.config import settings


def ensure_upload_dir() -> Path:
    path = Path(settings.upload_dir)
    if not path.is_absolute():
        path = Path(__file__).resolve().parents[2] / path
    path.mkdir(parents=True, exist_ok=True)
    return path


async def save_upload(file: UploadFile, subdir: str = "") -> str:
    base = ensure_upload_dir()
    target_dir = base / subdir if subdir else base
    target_dir.mkdir(parents=True, exist_ok=True)
    ext = Path(file.filename or "file").suffix or ".bin"
    name = f"{uuid.uuid4().hex}{ext}"
    dest = target_dir / name
    content = await file.read()
    dest.write_bytes(content)
    relative = f"{subdir}/{name}" if subdir else name
    return f"/uploads/{relative}"
