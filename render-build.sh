#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

echo "Installing Python deps..."
pip install -r backend/requirements.txt

echo "Building Vue frontend..."
cd frontend
npm ci
npm run build
cd "$ROOT"

echo "Copying frontend dist -> backend/static..."
rm -rf backend/static
mkdir -p backend/static
cp -R frontend/dist/. backend/static/

echo "Build complete."
