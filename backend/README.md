# LaburApp — Backend

API REST en FastAPI con SQLAlchemy 2.0 sobre PostgreSQL.

## Correr con Docker (recomendado)

Desde la raíz del repo:

```bash
docker compose up --build
```

- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- Health: http://localhost:8000/health

## Correr sin Docker

Necesitás un Postgres corriendo y la var `DATABASE_URL` apuntándole.

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements-dev.txt

# Copiá .env.example a .env en la raíz y ajustá DATABASE_URL a localhost
uvicorn app.main:app --reload
```

## Estructura

```
app/
  core/        config (settings), database (engine/session), security (JWT), deps
  models/      modelos ORM SQLAlchemy (una clase por tabla)
  schemas/     modelos Pydantic v2 (request/response)   ← Fase 2
  api/
    router.py  agrega todos los routers de dominio
    routes/    un módulo por dominio                    ← Fase 2
  main.py      app factory FastAPI
alembic/       migraciones                              ← Fase 2
tests/         pytest                                    ← Fase 2
```

## Notas

- En `ENVIRONMENT=local` las tablas se crean automáticamente al arrancar
  (`Base.metadata.create_all`). En producción se usa Alembic.
- Las credenciales y el `SECRET_KEY` se leen de variables de entorno, nunca
  se hardcodean (a diferencia del proyecto original de 2024).
