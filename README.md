# Residencial

App web mobile-first para gestión de condominios: junta de vecinos (admin), portal de residentes y personal (portería/mantenimiento).

## Stack

- **Backend:** FastAPI + SQLAlchemy + JWT + Gunicorn
- **Frontend:** Vue 3 + TypeScript + Pinia + Tailwind + Chart.js
- **DB:** SQLite (local) / PostgreSQL (Render u otro hosting)

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

## Desplegar en Render

El repo incluye `render.yaml` + `Dockerfile` (Blueprint). Una sola URL sirve el API y el frontend Vue.

### Pasos

1. Sube el proyecto a GitHub/GitLab.
2. En [Render](https://dashboard.render.com) → **New** → **Blueprint**.
3. Conecta el repo y confirma el blueprint (`render.yaml`).
4. Espera el build Docker (Node construye Vue; Python corre FastAPI).
5. Abre la URL del servicio (`https://residencial.onrender.com` o la que asigne Render).

### Qué crea el Blueprint

| Recurso | Nombre | Notas |
|---------|--------|-------|
| PostgreSQL | `residencial-db` | Plan Basic (Render ya no ofrece Postgres free) |
| Web (Docker) | `residencial` | Plan Free; se duerme con inactividad |

### Variables de entorno

| Variable | Descripción |
|----------|-------------|
| `DATABASE_URL` | Inyectada desde Postgres de Render |
| `SECRET_KEY` | Generada automáticamente |
| `CORS_ORIGINS` | `*` |
| `SEED_DEMO` | `true` la 1ª vez; luego cámbialo a `false` en el dashboard |
| `WEB_CONCURRENCY` | Workers de Gunicorn (default `2`) |

### Cuentas demo (si `SEED_DEMO=true`)

| Rol | Email | Password |
|-----|-------|----------|
| Admin | admin@example.com | admin123 |
| Vecino | ana@example.com | vecino123 |
| Staff | staff@example.com | staff123 |

### Alternativa: Postgres gratis externo

1. Crea DB en [Neon](https://neon.tech) o Supabase.
2. En el Web Service, define `DATABASE_URL` manualmente (quita el binding `fromDatabase` o crea el servicio a mano).
3. Build/Start siguen siendo el `Dockerfile`.

### Deploy manual sin Blueprint

- **Runtime:** Docker
- **Dockerfile path:** `./Dockerfile`
- **Health check:** `/health`
- Env vars: tabla de arriba + `DATABASE_URL`

### Notas

- El plan free del web se duerme; el primer request puede tardar ~30–60s.
- Archivos en `uploads/` son efímeros; para producción real usa S3/R2.
- Build local del mismo artefacto: `docker build -t residencial .`

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
