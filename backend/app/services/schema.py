from sqlalchemy import text

from app.core.database import Base, engine
import app.models  # noqa: F401


def ensure_schema() -> None:
    """Crea tablas nuevas y columnas extras en SQLite sin Alembic."""
    Base.metadata.create_all(bind=engine)
    if engine.dialect.name != "sqlite":
        return

    with engine.begin() as conn:
        cols = {row[1] for row in conn.execute(text("PRAGMA table_info(users)")).fetchall()}
        alterations = []
        if "phone_secondary" not in cols:
            alterations.append("ALTER TABLE users ADD COLUMN phone_secondary VARCHAR(40)")
        if "whatsapp" not in cols:
            alterations.append("ALTER TABLE users ADD COLUMN whatsapp VARCHAR(40)")
        if "show_in_directory" not in cols:
            alterations.append("ALTER TABLE users ADD COLUMN show_in_directory BOOLEAN DEFAULT 1")
        for stmt in alterations:
            conn.execute(text(stmt))
