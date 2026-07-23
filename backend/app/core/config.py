from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from pydantic_settings import BaseSettings, SettingsConfigDict

_ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


def normalize_database_url(url: str) -> str:
    """Normaliza URLs de Render/Neon/Supabase para SQLAlchemy + psycopg2."""
    if url.startswith("postgres://"):
        url = "postgresql+psycopg2://" + url[len("postgres://") :]
    elif url.startswith("postgresql://") and "+psycopg2" not in url and "+asyncpg" not in url:
        url = "postgresql+psycopg2://" + url[len("postgresql://") :]

    if url.startswith("sqlite"):
        return url

    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    is_local = host in {"localhost", "127.0.0.1", ""}
    query = dict(parse_qsl(parsed.query, keep_blank_values=True))
    if not is_local and "sslmode" not in query:
        query["sslmode"] = "require"
        url = urlunparse(parsed._replace(query=urlencode(query)))
    return url


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE) if _ENV_FILE.exists() else None,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = "sqlite:///./residencial.db"
    secret_key: str = "residencial-dev-secret-key"
    access_token_expire_minutes: int = 480
    algorithm: str = "HS256"
    cors_origins: str = "http://localhost:5173"
    upload_dir: str = "uploads"
    seed_demo: bool = False

    @property
    def sqlalchemy_database_url(self) -> str:
        return normalize_database_url(self.database_url)

    @property
    def cors_origin_list(self) -> list[str]:
        if self.cors_origins.strip() == "*":
            return ["*"]
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
