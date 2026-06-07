# CLAUDE.md — Contexto del proyecto LaburApp

> Este archivo lo lee Claude Code automáticamente al abrir una sesión en `C:\laburapp`.
> Es el punto de entrada para continuar el trabajo sin re-explicar nada.

## Qué es

**LaburApp** es un **marketplace de servicios / "changas"** (estilo Workana / TaskRabbit).
Un `Usuario` actúa a la vez como **cliente** (contrata servicios, deja reseñas) y como
**profesional** (publica servicios, gestiona su calendario de disponibilidad).

> "Laburo" (lunfardo argentino) = trabajo.

Es la **reconstrucción cloud-native** de un proyecto de facultad de 2024.
- Original: FastAPI + MySQL crudo (SQL con f-strings, sin ORM) + Angular.
- Zip original de referencia: `C:\Users\Juanc\Downloads\LaburApp-main.zip`.
- Objetivo de la reconstrucción: portfolio empleable + aprender GCP/Cloud Run/Kubernetes.

## Stack (decisiones ya tomadas — no re-preguntar)

| Capa | Tecnología |
|------|-----------|
| Backend | FastAPI · SQLAlchemy 2.0 (estilo `Mapped`/`mapped_column`) · Alembic · Pydantic v2 |
| Auth | JWT (python-jose) + bcrypt (passlib) |
| DB | PostgreSQL — local: docker-compose · prod: Cloud SQL |
| Frontend | React 19 · TypeScript · Vite · Tailwind CSS (reemplaza el Angular original) |
| Infra | Docker → **Cloud Run primero**, **GKE después** (k8s = fase de estudio) |
| Alcance v1 | **Paridad completa** con el dominio original |

## Dominio (10 tablas)

Nombres de campos en **español** por fidelidad al original.

```
Usuario ──< Servicio >── Categoria / SubCategoria
   │           │
   │           └──< Resena (calificacion 1-5)
   ├──< Calendario ──< Evento (slots de disponibilidad horaria)
   ├──< Contratacion >── Servicio / Evento
   ├──< MetodoDePago
   └──< Direccion
```

Tablas: `usuarios`, `categorias`, `subcategorias`, `servicios`, `calendarios`,
`eventos`, `contrataciones`, `resenas`, `metodos_de_pago`, `direcciones`.

## Estructura del repo

```
backend/
  app/
    core/        config (pydantic-settings), database (engine/session),
                 security (JWT/bcrypt), deps (get_db, get_current_user)
    models/      modelos ORM SQLAlchemy — un archivo por entidad
    schemas/     Pydantic v2 (request/response)        ← Fase 2 (vacío)
    api/
      router.py  agrega los routers de dominio
      routes/    un módulo por dominio                  ← Fase 2 (vacío)
    main.py      app factory FastAPI
  alembic/       migraciones                            ← Fase 2 (vacío)
  tests/         pytest                                 ← Fase 2 (vacío)
  Dockerfile · requirements.txt · requirements-dev.txt
frontend/        SPA React + Vite                       ← Fase 3 (vacío)
infra/
  cloudrun/      deploy Cloud Run + Cloud SQL           ← Fase 4 (vacío)
  k8s/           manifests GKE                          ← Fase 5 (vacío)
docker-compose.yml   local: postgres + api
```

## Estado actual — Fase 2 COMPLETA ✅

- **Fase 1**: core del backend, los **10 modelos ORM** con relaciones, app factory,
  Docker y docker-compose. Repo git inicializado.
- **Fase 2**: backend de dominio completo. Verificado con **29 tests pytest** (verdes)
  y **ruff** limpio.
  - **Schemas Pydantic v2** (`app/schemas/`): un módulo por dominio.
  - **Routers** (`app/api/routes/`), cableados en `app/api/router.py` bajo `/api/v1`:
    `auth` (register + login JWT/OAuth2), `usuarios` (me + perfil público),
    `categorias` (+ subcategorías), `servicios` (búsqueda con filtros + CRUD del dueño),
    `calendarios`, `eventos` (slots, validación de rango horario, dueño),
    `contrataciones` (rol cliente/profesional), `resenas` (recalcula
    `calificacion_promedio` del profesional), `metodos-de-pago`, `direcciones`.
    Total: **41 rutas**.
  - **Alembic** configurado (`backend/alembic.ini`, `alembic/env.py` que lee
    `settings.DATABASE_URL`) + migración inicial que crea las 10 tablas.
  - **Seed** idempotente de categorías: `python -m app.db.seed` (10 cats + 44 subcats).
  - **Tests**: `tests/conftest.py` usa SQLite in-memory (StaticPool) y override de
    `get_db`; setea `ENVIRONMENT=test` antes de importar la app para que el lifespan
    no toque Postgres.

### Roadmap

- [x] **Fase 1 — Fundación**: estructura, core, modelos ORM, Docker local
- [x] **Fase 2 — Backend dominio**: schemas Pydantic + routers + Alembic +
      seed de categorías + tests pytest
- [ ] **Fase 3 — Frontend**: React+Vite+Tailwind, auth, búsqueda de servicios,
      agenda, contrataciones
- [ ] **Fase 4 — Cloud Run**: build → Artifact Registry → Cloud Run + Cloud SQL + CI/CD
- [ ] **Fase 5 — GKE (estudio)**: manifests Deployment/Service/Ingress, HPA

**Próximo paso sugerido:** Fase 3, el **frontend** React+Vite+Tailwind, consumiendo
los endpoints de `/api/v1` (empezando por auth + búsqueda de servicios).

## Cómo correr

```bash
# Con Docker (cuando esté instalado):
docker compose up --build
# API http://localhost:8000 · Swagger http://localhost:8000/docs

# Sin Docker (verificación local):
cd backend
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements-dev.txt
# crear .env desde .env.example, apuntando DATABASE_URL a un Postgres local
uvicorn app.main:app --reload

# Migraciones (producción / Postgres real):
alembic upgrade head            # aplica el esquema
alembic revision --autogenerate -m "mensaje"   # nueva migración

# Seed de categorías (idempotente):
python -m app.db.seed

# Tests (usan SQLite in-memory, no requieren Postgres):
pytest
ruff check app tests alembic
```

## Convenciones y aprendizajes (importante)

- **Secrets por entorno**: `SECRET_KEY`, `DATABASE_URL` se leen de env/.env. NUNCA
  hardcodear (el original tenía credenciales y secret en el código).
- **Nada de SQL a mano**: todo vía ORM / queries de SQLAlchemy.
- En `ENVIRONMENT=local` las tablas se crean con `Base.metadata.create_all` al
  arrancar; en producción las maneja **Alembic**.
- Cada modelo nuevo debe importarse en `app/models/__init__.py` para que Alembic
  y `create_all` lo descubran.
- **Docker NO está instalado** en esta máquina (ni en PATH de bash ni PowerShell).
  Para verificar localmente: usar `backend/.venv` (gitignored) con Python 3.12.
  Para `docker compose up` real hace falta instalar Docker Desktop.
- Shell por defecto: **PowerShell** en Windows (sintaxis `$env:VAR`, no `$VAR`).
- Mantener nombres de dominio en español; código/comentarios pueden mezclar.

## Errores conocidos del original (NO replicar)

- Rutas duplicadas y typos (`categwaorias`, tabla `contratos` vs `contrataciones`).
- `UPDATE servicios ... SET locality = %s,` con coma colgante antes de `WHERE`.
- Orden de parámetros desalineado en varios `cursor.execute`.
- `AuthResponse` devolvía el `password` hasheado al cliente (no hacerlo).
