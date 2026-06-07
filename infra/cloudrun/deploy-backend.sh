#!/usr/bin/env bash
# Construye y despliega la API (FastAPI) en Cloud Run.
#   ./deploy-backend.sh
set -euo pipefail

cd "$(dirname "$0")"
# shellcheck disable=SC1091
source .env

REPO_ROOT="$(git rev-parse --show-toplevel)"
TAG="$(git -C "$REPO_ROOT" rev-parse --short HEAD 2>/dev/null || date +%s)"
IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${AR_REPO}/${API_SERVICE}:${TAG}"

INSTANCE_CONNECTION_NAME="$(gcloud sql instances describe "$DB_INSTANCE" \
  --format='value(connectionName)')"

echo "▶ Build de la imagen API: $IMAGE"
gcloud builds submit "$REPO_ROOT/backend" --tag "$IMAGE"

# Si el frontend ya está desplegado, permitimos su origen en CORS.
WEB_URL="$(gcloud run services describe "$WEB_SERVICE" --region="$REGION" \
  --format='value(status.url)' 2>/dev/null || true)"
CORS="${WEB_URL:-http://localhost:5173}"

echo "▶ Deploy de $API_SERVICE en Cloud Run…"
gcloud run deploy "$API_SERVICE" \
  --image="$IMAGE" \
  --region="$REGION" \
  --platform=managed \
  --allow-unauthenticated \
  --add-cloudsql-instances="$INSTANCE_CONNECTION_NAME" \
  --set-env-vars="ENVIRONMENT=production,BACKEND_CORS_ORIGINS=${CORS}" \
  --set-secrets="DATABASE_URL=DATABASE_URL:latest,SECRET_KEY=SECRET_KEY:latest"

API_URL="$(gcloud run services describe "$API_SERVICE" --region="$REGION" \
  --format='value(status.url)')"
echo
echo "✅ API desplegada: $API_URL"
echo "   Docs: $API_URL/docs"
