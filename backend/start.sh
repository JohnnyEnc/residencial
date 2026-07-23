#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
export PYTHONPATH=.

# Por defecto: SQLite local al contenedor (sin servicios externos).
export DATABASE_URL="${DATABASE_URL:-sqlite:////app/data/residencial.db}"

if [[ "${DATABASE_URL}" == sqlite* ]]; then
  mkdir -p /app/data "$(dirname "${DATABASE_URL#sqlite:///}")" 2>/dev/null || mkdir -p /app/data
  echo "Using SQLite at ${DATABASE_URL}"
  echo "Creating tables..."
  python - <<'PY'
from app.core.database import Base, engine
import app.models  # noqa: F401

Base.metadata.create_all(bind=engine)
print("Tables ready")
PY
else
  echo "Using Postgres; running Alembic migrations..."
  alembic upgrade head
fi

if [ "${SEED_DEMO:-false}" = "true" ]; then
  echo "Seeding demo data (if empty)..."
  python scripts/seed.py
fi

PORT="${PORT:-8000}"
# SQLite + varios workers causa bloqueos; forzar 1 worker si es sqlite.
if [[ "${DATABASE_URL}" == sqlite* ]]; then
  WEB_CONCURRENCY=1
fi

echo "Starting Residencial on port ${PORT} (workers=${WEB_CONCURRENCY:-2})..."
exec gunicorn app.main:app \
  -k uvicorn.workers.UvicornWorker \
  --bind "0.0.0.0:${PORT}" \
  --workers "${WEB_CONCURRENCY:-2}" \
  --timeout 120
