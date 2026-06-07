#!/usr/bin/env bash
# Provisión one-time para GKE: cluster Autopilot, Cloud SQL (si no existe),
# y Workload Identity (GSA <-> KSA) para que el proxy llegue a Cloud SQL.
# Idempotente.
#
#   cp .env.example .env && edita .env
#   ./setup-cluster.sh
set -euo pipefail

cd "$(dirname "$0")"
# shellcheck disable=SC1091
source .env

gcloud config set project "$PROJECT_ID" >/dev/null

echo "▶ Habilitando APIs…"
gcloud services enable \
  container.googleapis.com \
  sqladmin.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com

# ─── Artifact Registry (reusa si existe) ───────────────────
if ! gcloud artifacts repositories describe "$AR_REPO" --location="$REGION" >/dev/null 2>&1; then
  gcloud artifacts repositories create "$AR_REPO" \
    --repository-format=docker --location="$REGION"
fi

# ─── Cluster GKE Autopilot ─────────────────────────────────
if ! gcloud container clusters describe "$CLUSTER" --region="$REGION" >/dev/null 2>&1; then
  echo "▶ Creando cluster Autopilot '$CLUSTER' (tarda ~10 min)…"
  gcloud container clusters create-auto "$CLUSTER" --region="$REGION"
else
  echo "✓ Cluster '$CLUSTER' ya existe"
fi

# ─── Cloud SQL (si no existe) ──────────────────────────────
if ! gcloud sql instances describe "$DB_INSTANCE" >/dev/null 2>&1; then
  echo "▶ Creando Cloud SQL '$DB_INSTANCE' (tarda varios minutos)…"
  gcloud sql instances create "$DB_INSTANCE" \
    --database-version=POSTGRES_16 --tier="$DB_TIER" --region="$REGION"
fi
gcloud sql databases describe "$DB_NAME" --instance="$DB_INSTANCE" >/dev/null 2>&1 \
  || gcloud sql databases create "$DB_NAME" --instance="$DB_INSTANCE"

# Password del usuario (guardado en Secret Manager para no perderlo).
if ! gcloud secrets describe DB_PASSWORD >/dev/null 2>&1; then
  DB_PASSWORD="$(openssl rand -base64 24 | tr -d '/+=' | cut -c1-24)"
  printf '%s' "$DB_PASSWORD" | gcloud secrets create DB_PASSWORD --data-file=-
  gcloud sql users create "$DB_USER" --instance="$DB_INSTANCE" --password="$DB_PASSWORD" \
    || gcloud sql users set-password "$DB_USER" --instance="$DB_INSTANCE" --password="$DB_PASSWORD"
fi

# ─── Workload Identity ─────────────────────────────────────
GSA_EMAIL="${GSA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
if ! gcloud iam service-accounts describe "$GSA_EMAIL" >/dev/null 2>&1; then
  gcloud iam service-accounts create "$GSA_NAME" --display-name="chambapp GKE"
fi
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:${GSA_EMAIL}" --role=roles/cloudsql.client --condition=None >/dev/null

# Permite que la KSA chambapp/chambapp impersone la GSA.
gcloud iam service-accounts add-iam-policy-binding "$GSA_EMAIL" \
  --role=roles/iam.workloadIdentityUser \
  --member="serviceAccount:${PROJECT_ID}.svc.id.goog[chambapp/chambapp]" >/dev/null

echo
echo "✅ Cluster e infraestructura listos."
echo "   Próximo: ./deploy.sh"
