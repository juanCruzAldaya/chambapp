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
      seed de categorías + tests pytest (30 tests)
- [x] **Fase 3 — Frontend**: React 19 + Vite + Tailwind v4, auth, búsqueda de
      servicios, detalle + contratar, publicar, agenda, contrataciones, perfil
- [x] **Fase 4 — Cloud Run**: Dockerfiles (API + frontend nginx), Cloud SQL,
      Artifact Registry, Secret Manager, CI/CD (Cloud Build + GitHub Actions)
- [x] **Fase 5 — GKE (estudio)**: manifests en `infra/k8s/` (Deployment + sidecar
      Cloud SQL proxy, Service, Ingress, HPA, Job de migración, Workload Identity)
      + scripts (`setup-cluster.sh`, `deploy.sh`). NO desplegado (GKE tiene costo).

**Proyecto completo.** Las 5 fases están hechas. Material de estudio en
`docs/estudio/` (un HTML por fase, autocontenido, foco en backend + front + infra).

### Infra Fase 5 (`infra/k8s/`)

- **No se desplegó** a propósito: GKE no tiene free tier (cluster + Cloud SQL +
  Load Balancer cuestan). Queda listo para aplicar con `setup-cluster.sh` + `deploy.sh`.
- Cloud SQL por **sidecar** (Cloud SQL Auth Proxy) + **Workload Identity** (sin claves).
- **Ingress** único con routing por path (`/api/*`→api, resto→web) ⇒ mismo origen,
  sin CORS; el frontend se buildea con `VITE_API_URL=/api/v1`.
- Migraciones en un **Job** (no en cada réplica); HPA por CPU.

### Material de estudio (`docs/estudio/`)

- `index.html` + `fase-1..5.html` + `styles.css`. HTMLs autocontenidos (se abren con
  doble clic, sin internet), con recuadros de concepto/tip/ojo/entrevista. Pensados
  para estudiar a fondo y para defender el proyecto en entrevistas.

### Infra Fase 4 (`infra/cloudrun/`)

- **Dos servicios Cloud Run**: `chambapp-api` (FastAPI) y `chambapp-web` (nginx
  sirviendo la SPA). Imágenes en Artifact Registry.
- **backend/entrypoint.sh**: corre `alembic upgrade head` (y seed opcional con
  `SEED_ON_START=true`) antes de uvicorn. En prod NO se usa `create_all`.
- **Cloud SQL** (Postgres) por unix socket; `DATABASE_URL` y `SECRET_KEY` en
  **Secret Manager** (inyectados con `--set-secrets`).
- **frontend/Dockerfile** multi-stage (Vite build → nginx en `$PORT`);
  `VITE_API_URL` se hornea en build con la URL real de la API.
- Scripts: `setup.sh` (provisión one-time), `deploy-backend.sh`, `deploy-frontend.sh`.
- **CI/CD**: `.github/workflows/ci.yml` (ruff+pytest+build en cada PR) y
  `deploy.yml` (CD a Cloud Run vía Cloud Build + Workload Identity Federation,
  activable con la variable `DEPLOY_ENABLED=true`). Ver `infra/cloudrun/README.md`.
- **docker-compose**: el servicio `api` resetea `entrypoint: []` para mantener
  hot-reload en dev (no corre migraciones).

> Nota Fase 3→backend: se agregó un endpoint público `GET /usuarios/{id}/calendarios`
> (disponibilidad del profesional) para habilitar el flujo de contratación por turnos.
> El frontend vive en `frontend/` (ver su README). Stack: cliente `fetch` tipado +
> AuthContext (JWT en localStorage), proxy de Vite `/api → :8000` en dev.

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

# Frontend (en otra terminal, con el backend corriendo en :8000):
cd frontend
npm install
npm run dev        # http://localhost:5173 (proxea /api -> :8000)
npm run build      # tsc -b && vite build
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
