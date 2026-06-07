#!/usr/bin/env bash
# Provisión one-time de la infraestructura en GCP para chambapp.
# Idempotente: se puede correr varias veces sin romper nada.
#
#   cp .env.example .env && edita .env
#   ./setup.sh
set -euo pipefail

cd "$(dirname "$0")"
# shellcheck disable=SC1091
source .env

echo "▶ Proyecto: $PROJECT_ID  ·  Región: $REGION"
gcloud config set project "$PROJECT_ID" >/dev/null

# ─── 1. Habilitar APIs ─────────────────────────────────────
echo "▶ Habilitando APIs…"
gcloud services enable \
  run.googleapis.com \
  sqladmin.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  secretmanager.googleapis.com

# ─── 2. Artifact Registry ──────────────────────────────────
if ! gcloud artifacts repositories describe "$AR_REPO" --location="$REGION" >/dev/null 2>&1; then
  echo "▶ Creando repo de Artifact Registry '$AR_REPO'…"
  gcloud artifacts repositories create "$AR_REPO" \
    --repository-format=docker \
    --location="$REGION" \
    --description="Imágenes de chambapp"
else
  echo "✓ Artifact Registry '$AR_REPO' ya existe"
fi

# ─── 3. Cloud SQL (Postgres) ───────────────────────────────
if ! gcloud sql instances describe "$DB_INSTANCE" >/dev/null 2>&1; then
  echo "▶ Creando instancia Cloud SQL '$DB_INSTANCE' (puede tardar varios minutos)…"
  gcloud sql instances create "$DB_INSTANCE" \
    --database-version=POSTGRES_16 \
    --tier="$DB_TIER" \
    --region="$REGION" \
    --storage-auto-increase
else
  echo "✓ Instancia Cloud SQL '$DB_INSTANCE' ya existe"
fi

if ! gcloud sql databases describe "$DB_NAME" --instance="$DB_INSTANCE" >/dev/null 2>&1; then
  echo "▶ Creando base '$DB_NAME'…"
  gcloud sql databases create "$DB_NAME" --instance="$DB_INSTANCE"
else
  echo "✓ Base '$DB_NAME' ya existe"
fi

INSTANCE_CONNECTION_NAME="$(gcloud sql instances describe "$DB_INSTANCE" \
  --format='value(connectionName)')"
echo "▶ INSTANCE_CONNECTION_NAME=$INSTANCE_CONNECTION_NAME"

# ─── 4. Secrets (password DB, DATABASE_URL, SECRET_KEY) ─────
create_secret() {
  local name="$1" value="$2"
  if ! gcloud secrets describe "$name" >/dev/null 2>&1; then
    printf '%s' "$value" | gcloud secrets create "$name" --data-file=-
    echo "▶ Secret '$name' creado"
  else
    echo "✓ Secret '$name' ya existe (no se sobreescribe)"
  fi
}

if ! gcloud secrets describe DB_PASSWORD >/dev/null 2>&1; then
  DB_PASSWORD="$(openssl rand -base64 24 | tr -d '/+=' | cut -c1-24)"
  create_secret DB_PASSWORD "$DB_PASSWORD"
  echo "▶ Seteando password del usuario '$DB_USER'…"
  gcloud sql users create "$DB_USER" --instance="$DB_INSTANCE" --password="$DB_PASSWORD" \
    || gcloud sql users set-password "$DB_USER" --instance="$DB_INSTANCE" --password="$DB_PASSWORD"
else
  DB_PASSWORD="$(gcloud secrets versions access latest --secret=DB_PASSWORD)"
  echo "✓ DB_PASSWORD ya existe"
fi

# DATABASE_URL con conexión por unix socket de Cloud SQL.
DATABASE_URL="postgresql+psycopg2://${DB_USER}:${DB_PASSWORD}@/${DB_NAME}?host=/cloudsql/${INSTANCE_CONNECTION_NAME}"
create_secret DATABASE_URL "$DATABASE_URL"
create_secret SECRET_KEY "$(openssl rand -hex 32)"

# ─── 5. IAM para la service account de runtime de Cloud Run ──
PROJECT_NUMBER="$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')"
RUNTIME_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"
echo "▶ Otorgando permisos a $RUNTIME_SA…"
for role in roles/secretmanager.secretAccessor roles/cloudsql.client; do
  gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:${RUNTIME_SA}" --role="$role" \
    --condition=None >/dev/null
done

echo
echo "✅ Setup completo."
echo "   Próximo: ./deploy-backend.sh  y luego  ./deploy-frontend.sh"
