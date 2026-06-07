# LaburApp

Marketplace de servicios profesionales ("changas") que conecta **clientes** que necesitan un trabajo con **profesionales** que lo ofrecen. Reconstrucción 2025 de un proyecto de facultad (2024), ahora con arquitectura cloud-native.

> "Laburo" (lunfardo argentino) = trabajo. LaburApp = la app para conseguir laburo.

## Stack

| Capa | Tecnología |
|------|-----------|
| **Backend** | FastAPI · SQLAlchemy 2.0 · Alembic · Pydantic v2 · JWT (bcrypt) |
| **Base de datos** | PostgreSQL (local: Docker · prod: Cloud SQL) |
| **Frontend** | React 19 · TypeScript · Vite · Tailwind CSS |
| **Infra** | Docker · Cloud Run · Artifact Registry · (GKE como fase de estudio) |
| **CI/CD** | GitHub Actions / Cloud Build |

## Dominio

```
Usuario ──< Servicio >── Categoria / SubCategoria
   │           │
   │           └──< Resena
   ├──< Calendario ──< Evento (slots de disponibilidad)
   ├──< Contratacion >── Servicio / Evento
   ├──< MetodoDePago
   └──< Direccion
```

Un usuario puede actuar como **cliente** (contrata servicios, deja reseñas) y como **profesional** (publica servicios, gestiona su calendario).

## Desarrollo local

```bash
# Levanta Postgres + API con hot-reload
docker compose up --build

# API:        http://localhost:8000
# Swagger:    http://localhost:8000/docs
# Postgres:   localhost:5432
```

Ver [backend/README.md](backend/README.md) para correr el backend sin Docker.

## Estructura

```
backend/    API FastAPI (app/core, app/models, app/schemas, app/api)
frontend/   SPA React + Vite
infra/      cloudrun/ (deploy) · k8s/ (manifests GKE)
```

## Roadmap

- [x] Fase 1 — Fundación: estructura, core, modelos ORM, Docker local
- [ ] Fase 2 — Backend dominio completo + Alembic + tests
- [ ] Fase 3 — Frontend React
- [ ] Fase 4 — Deploy Cloud Run + Cloud SQL + CI/CD
- [ ] Fase 5 — GKE (estudio)
