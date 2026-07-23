# Residencial

App web mobile-first para gestión de condominios: junta de vecinos (admin), portal de residentes y personal (portería/mantenimiento).

## Stack

- **Backend:** FastAPI + SQLAlchemy + JWT + Gunicorn
- **Frontend:** Vue 3 + TypeScript + Pinia + Tailwind + Chart.js
- **DB:** SQLite (local) / PostgreSQL gratis en [Neon](https://neon.tech) (producción en Render)

## Arranque local

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=. python scripts/seed.py
uvicorn app.main:app --reload --port 8000
```

### Frontend (dev)

```bash
cd frontend
npm install
npm run dev
```

App local: http://127.0.0.1:5173 · API: http://127.0.0.1:8000/docs

## Desplegar en Render (100% free)

Render ya no ofrece Postgres gratis. El Blueprint usa:

- **Web Service free** (Docker) en Render
- **Postgres free** en Neon (o Supabase)

### 1. Crear la base en Neon (gratis)

1. Entra a [neon.tech](https://neon.tech) y crea un proyecto.
2. Copia la **connection string** (formato `postgresql://...`).
3. Asegúrate de que incluya SSL (Neon suele traer `sslmode=require`; si no, la app lo añade sola).

### 2. Desplegar el Blueprint en Render

1. [Render](https://dashboard.render.com) → **New** → **Blueprint**.
2. Conecta el repo `residencial`.
3. Cuando pida **`DATABASE_URL`**, pega la connection string de Neon.
4. Confirma el deploy.

Quedará una sola URL con frontend + API (`https://residencial.onrender.com` o similar).

### Variables de entorno

| Variable | Descripción |
|----------|-------------|
| `DATABASE_URL` | Connection string de Neon (obligatoria) |
| `SECRET_KEY` | Generada automáticamente |
| `CORS_ORIGINS` | `*` |
| `SEED_DEMO` | `true` la 1ª vez; luego cámbialo a `false` |
| `WEB_CONCURRENCY` | Workers de Gunicorn (default `2`) |

### Cuentas demo (si `SEED_DEMO=true`)

| Rol | Email | Password |
|-----|-------|----------|
| Admin | admin@example.com | admin123 |
| Vecino | ana@example.com | vecino123 |
| Staff | staff@example.com | staff123 |

### Alternativa: Supabase

Misma idea: crea un proyecto gratis, copia la URI de Postgres y úsala como `DATABASE_URL`.

### Notas

- El plan free del web se duerme; el primer request puede tardar ~30–60s.
- Archivos en `uploads/` son efímeros; para producción real usa S3/R2.
- Build local: `docker build -t residencial .`

## Funcionalidades MVP

- Login por rol (admin / resident / staff)
- Viviendas, usuarios, cuotas y conciliación de pagos
- Reportes con asignación a personal
- Avisos / comunicados
- Dashboard admin con gráficos de deudas, pagos y morosos

## Estructura

```
residencial/
  Dockerfile
  render.yaml
  render-build.sh
  docker-compose.yml
  backend/
    start.sh
    app/
  frontend/
```
