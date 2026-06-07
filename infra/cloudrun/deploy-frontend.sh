#!/usr/bin/env bash
# Construye y despliega el frontend (SPA + nginx) en Cloud Run.
# Hornea la URL de la API en el bundle y actualiza el CORS de la API.
#   ./deploy-frontend.sh
set -euo pipefail

cd "$(dirname "$0")"
# shellcheck disable=SC1091
source .env

REPO_ROOT="$(git rev-parse --show-toplevel)"
TAG="$(git -C "$REPO_ROOT" rev-parse --short HEAD 2>/dev/null || date +%s)"
IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${AR_REPO}/${WEB_SERVICE}:${TAG}"

# La API tiene que estar desplegada primero (para conocer su URL).
API_URL="$(gcloud run services describe "$API_SERVICE" --region="$REGION" \
  --format='value(status.url)' 2>/dev/null || true)"
if [ -z "$API_URL" ]; then
  echo "✗ No encuentro la API '$API_SERVICE'. Corré primero ./deploy-backend.sh" >&2
  exit 1
fi
VITE_API_URL="${API_URL}/api/v1"

echo "▶ Build del frontend (VITE_API_URL=$VITE_API_URL)…"
gcloud builds submit "$REPO_ROOT/frontend" \
  --config="$(pwd)/web.build.yaml" \
  --substitutions="_IMAGE=${IMAGE},_VITE_API_URL=${VITE_API_URL}"

echo "▶ Deploy de $WEB_SERVICE en Cloud Run…"
gcloud run deploy "$WEB_SERVICE" \
  --image="$IMAGE" \
  --region="$REGION" \
  --platform=managed \
  --allow-unauthenticated

WEB_URL="$(gcloud run services describe "$WEB_SERVICE" --region="$REGION" \
  --format='value(status.url)')"

# Ahora que conocemos la URL del front, la habilitamos en el CORS de la API.
echo "▶ Actualizando CORS de la API con $WEB_URL…"
gcloud run services update "$API_SERVICE" \
  --region="$REGION" \
  --update-env-vars="BACKEND_CORS_ORIGINS=${WEB_URL}"

echo
echo "✅ Frontend desplegado: $WEB_URL"
