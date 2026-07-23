#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
export PYTHONPATH=.

echo "Running migrations..."
alembic upgrade head

if [ "${SEED_DEMO:-false}" = "true" ]; then
  echo "Seeding demo data (if empty)..."
  python scripts/seed.py
fi

PORT="${PORT:-8000}"
echo "Starting Residencial on port ${PORT}..."
exec gunicorn app.main:app \
  -k uvicorn.workers.UvicornWorker \
  --bind "0.0.0.0:${PORT}" \
  --workers "${WEB_CONCURRENCY:-2}" \
  --timeout 120
