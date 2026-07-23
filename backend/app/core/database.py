from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

url = settings.sqlalchemy_database_url
connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}

# Neon (serverless) se lleva mejor con pool pequeño + pre_ping.
engine_kwargs: dict = {"pool_pre_ping": True, "connect_args": connect_args}
if url.startswith("postgresql"):
    engine_kwargs.update(pool_size=5, max_overflow=5, pool_recycle=300)

engine = create_engine(url, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
