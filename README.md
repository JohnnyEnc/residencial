# Residencial

App web mobile-first para gestión de condominios: junta de vecinos (admin), portal de residentes y personal (portería/mantenimiento).

## Stack

- **Backend:** FastAPI + SQLAlchemy + JWT + Gunicorn
- **Frontend:** Vue 3 + TypeScript + Pinia + Tailwind + Chart.js
- **DB:** SQLite (local y en Render free; sin registros extra)

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

## Desplegar en Render (gratis, sin Neon ni nada extra)

1. [Render](https://dashboard.render.com) → **New** → **Blueprint**
2. Conecta el repo `residencial`
3. Confirma el deploy (no pide base de datos externa)

Usa **SQLite** dentro del servicio. Al arrancar crea tablas y, si `SEED_DEMO=true`, carga las cuentas demo.

### Importante

En el plan free de Render el disco es **efímero**: si el servicio se redespliega o se recrea el contenedor, los datos de SQLite se reinician (y el seed vuelve a cargar el demo). Sirve bien para demo/MVP; para datos permanentes después se puede migrar a Postgres.

### Variables de entorno

| Variable | Valor |
|----------|--------|
| `DATABASE_URL` | `sqlite:////app/data/residencial.db` |
| `SECRET_KEY` | Generada automáticamente |
| `SEED_DEMO` | `true` (demo); luego puedes poner `false` |
| `WEB_CONCURRENCY` | `1` (necesario con SQLite) |

### Cuentas demo

| Rol | Email | Password |
|-----|-------|----------|
| Admin | admin@example.com | admin123 |
| Vecino | ana@example.com | vecino123 |
| Staff | staff@example.com | staff123 |

### Notas

- El plan free se duerme con inactividad; el primer request puede tardar ~30–60s.
- Archivos en `uploads/` también son efímeros.

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
  backend/
  frontend/
```
