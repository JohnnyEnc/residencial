#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
export PYTHONPATH=.

# Si DATABASE_URL viene vacío (Blueprint sync:false sin valor), forzar SQLite.
if [ -z "${DATABASE_URL:-}" ]; then
  export DATABASE_URL="sqlite:////app/data/residencial.db"
fi

mkdir -p /app/data /app/uploads

if [[ "${DATABASE_URL}" == sqlite* ]]; then
  echo "Using SQLite at ${DATABASE_URL}"
  echo "Creating tables..."
  python - <<'PY'
from app.services.schema import ensure_schema

ensure_schema()
print("Tables ready")
PY
else
  echo "Using Postgres; running Alembic migrations..."
  alembic upgrade head
  python - <<'PY'
from app.services.schema import ensure_schema

ensure_schema()
print("Schema ensured")
PY
fi

# Sembrar usuarios demo si la DB está vacía (idempotente).
echo "Running seed (no-op if users already exist)..."
python scripts/seed.py

PORT="${PORT:-8000}"
if [[ "${DATABASE_URL}" == sqlite* ]]; then
  WEB_CONCURRENCY=1
fi

echo "Starting Residencial on port ${PORT} (workers=${WEB_CONCURRENCY:-2})..."
exec gunicorn app.main:app \
  -k uvicorn.workers.UvicornWorker \
  --bind "0.0.0.0:${PORT}" \
  --workers "${WEB_CONCURRENCY:-2}" \
  --timeout 120
