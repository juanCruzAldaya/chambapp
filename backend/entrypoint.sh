#!/bin/sh
# Entrypoint del contenedor de la API.
# En producción el esquema lo maneja Alembic (no create_all).
set -e

# Aplica migraciones pendientes (desactivable con RUN_MIGRATIONS=false).
if [ "${RUN_MIGRATIONS:-true}" = "true" ]; then
  echo "→ Aplicando migraciones (alembic upgrade head)…"
  alembic upgrade head
fi

# Seed idempotente de categorías (opcional, off por defecto).
if [ "${SEED_ON_START:-false}" = "true" ]; then
  echo "→ Seed de categorías…"
  python -m app.db.seed
fi

# Cloud Run inyecta $PORT (default 8080).
echo "→ Iniciando uvicorn en :${PORT:-8080}…"
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8080}"
