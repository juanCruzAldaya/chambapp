#!/usr/bin/env bash
# Build de imágenes + despliegue de chambapp en el cluster GKE.
# Asume que ./setup-cluster.sh ya corrió.
#   ./deploy.sh
set -euo pipefail

cd "$(dirname "$0")"
# shellcheck disable=SC1091
source .env

REPO_ROOT="$(git rev-parse --show-toplevel)"
TAG="$(git -C "$REPO_ROOT" rev-parse --short HEAD 2>/dev/null || date +%s)"
AR="${REGION}-docker.pkg.dev/${PROJECT_ID}/${AR_REPO}"
export API_IMAGE="${AR}/chambapp-api:${TAG}"
export WEB_IMAGE="${AR}/chambapp-web:${TAG}"
export GSA_EMAIL="${GSA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
export INSTANCE_CONNECTION_NAME="$(gcloud sql instances describe "$DB_INSTANCE" \
  --format='value(connectionName)')"

# ─── 1. Build + push de imágenes ───────────────────────────
echo "▶ Build API → $API_IMAGE"
gcloud builds submit "$REPO_ROOT/backend" --tag "$API_IMAGE"

echo "▶ Build WEB → $WEB_IMAGE (VITE_API_URL=/api/v1, mismo origen)"
gcloud builds submit "$REPO_ROOT/frontend" \
  --config="$(pwd)/../cloudrun/web.build.yaml" \
  --substitutions="_IMAGE=${WEB_IMAGE},_VITE_API_URL=/api/v1"

# ─── 2. Credenciales del cluster ───────────────────────────
gcloud container clusters get-credentials "$CLUSTER" --region="$REGION"

# ─── 3. Namespace + ServiceAccount (Workload Identity) ─────
kubectl apply -f 01-namespace.yaml
envsubst < 02-serviceaccount.yaml | kubectl apply -f -

# ─── 4. Secret con DATABASE_URL + SECRET_KEY ───────────────
DB_PASSWORD="$(gcloud secrets versions access latest --secret=DB_PASSWORD)"
DATABASE_URL="postgresql+psycopg2://${DB_USER}:${DB_PASSWORD}@127.0.0.1:5432/${DB_NAME}"
SECRET_KEY="$(gcloud secrets versions access latest --secret=SECRET_KEY 2>/dev/null \
  || openssl rand -hex 32)"
kubectl -n chambapp create secret generic chambapp-secrets \
  --from-literal=DATABASE_URL="$DATABASE_URL" \
  --from-literal=SECRET_KEY="$SECRET_KEY" \
  --dry-run=client -o yaml | kubectl apply -f -

# ─── 5. Migraciones (Job de una sola corrida) ──────────────
echo "▶ Corriendo migraciones…"
kubectl -n chambapp delete job chambapp-migrate --ignore-not-found
envsubst < 06-migrate-job.yaml | kubectl apply -f -
kubectl -n chambapp wait --for=condition=complete job/chambapp-migrate --timeout=300s

# ─── 6. Deployments + Services + Ingress + HPA ─────────────
envsubst < 04-backend.yaml  | kubectl apply -f -
envsubst < 05-frontend.yaml | kubectl apply -f -
kubectl apply -f 07-ingress.yaml
kubectl apply -f 08-hpa.yaml

echo
echo "✅ Desplegado. La IP pública del Ingress tarda unos minutos en aparecer:"
echo "   kubectl -n chambapp get ingress chambapp -w"
