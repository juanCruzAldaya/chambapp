# Despliegue en Cloud Run (Fase 4)

Infraestructura de **chambapp** en GCP: dos servicios Cloud Run (API + frontend),
Cloud SQL (Postgres), Artifact Registry para las imágenes, secrets en Secret
Manager y CI/CD con Cloud Build + GitHub Actions.

```
                 ┌──────────────┐        ┌──────────────┐
   navegador ──► │ chambapp-web │ ─CORS► │ chambapp-api │ ─unix socket─► Cloud SQL
                 │  (nginx SPA) │        │  (FastAPI)   │                (Postgres)
                 └──────────────┘        └──────────────┘
                        ▲                        ▲
                   Artifact Registry  ◄── Cloud Build ──► Secret Manager
```

## Requisitos

- [gcloud CLI](https://cloud.google.com/sdk/docs/install) autenticado (`gcloud auth login`).
- Un proyecto GCP con facturación habilitada.
- `openssl` (para generar secrets) y `git`.

> Los scripts son bash. En Windows usar **Git Bash** o WSL.

## 1. Configurar variables

```bash
cd infra/cloudrun
cp .env.example .env
# editar .env: completar PROJECT_ID (y ajustar región/nombres si querés)
```

## 2. Provisión one-time

```bash
./setup.sh
```

Crea (idempotente): habilita APIs, repo de Artifact Registry, instancia Cloud SQL
+ base + usuario, los secrets `DB_PASSWORD`, `DATABASE_URL` y `SECRET_KEY`, y los
permisos IAM (`secretAccessor` + `cloudsql.client`) para la service account de
runtime de Cloud Run.

> La instancia Cloud SQL tarda varios minutos en crearse la primera vez.

## 3. Desplegar

El orden importa: **primero la API** (el frontend hornea su URL en el bundle).

```bash
./deploy-backend.sh     # build + deploy de la API; corre alembic upgrade al arrancar
./deploy-frontend.sh    # build (con VITE_API_URL=<api>/api/v1) + deploy + ajusta CORS
```

Al terminar tenés las dos URLs `*.run.app`. La API expone `/docs`.

### Cargar las categorías (seed)

El seed no corre solo en prod. Una opción simple es redeployar la API una vez con
el flag de seed activado:

```bash
gcloud run services update chambapp-api --region=us-central1 \
  --update-env-vars=SEED_ON_START=true
# (luego conviene volver a poner SEED_ON_START=false)
```

## Cómo funciona cada pieza

| Pieza | Detalle |
|-------|---------|
| **Migraciones** | `backend/entrypoint.sh` corre `alembic upgrade head` al iniciar el contenedor (en prod NO se usa `create_all`). |
| **Conexión a la DB** | Por unix socket de Cloud SQL: `...@/<db>?host=/cloudsql/<INSTANCE_CONNECTION_NAME>`, montado con `--add-cloudsql-instances`. |
| **Secrets** | `DATABASE_URL` y `SECRET_KEY` se inyectan con `--set-secrets` desde Secret Manager (nunca en texto plano). |
| **Frontend** | `Dockerfile` multi-stage: Vite build → nginx. `VITE_API_URL` se hornea en build. nginx escucha `$PORT` (envsubst de la imagen oficial). |
| **CORS** | `deploy-frontend.sh` actualiza `BACKEND_CORS_ORIGINS` de la API con la URL real del front. |

## CI/CD

### CI (siempre activo) — `.github/workflows/ci.yml`
En cada push/PR: lint + tests del backend (ruff, pytest) y typecheck + build del
frontend. No necesita ningún secreto.

### CD a Cloud Run — `.github/workflows/deploy.yml`
Despliega en push a `main` vía Cloud Build, usando **Workload Identity Federation**
(sin claves de service account). Está desactivado hasta que configures:

1. **Repo variable** `DEPLOY_ENABLED=true` (Settings → Variables → Actions).
2. **Secrets**: `GCP_PROJECT_ID`, `GCP_WORKLOAD_IDENTITY_PROVIDER`, `GCP_DEPLOY_SA`.

Setup de WIF (one-time):

```bash
PROJECT_ID=<tu-proyecto>
PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')
REPO=juanCruzAldaya/chambapp   # owner/repo de GitHub

# Service account de deploy
gcloud iam service-accounts create chambapp-deploy --project="$PROJECT_ID"
DEPLOY_SA="chambapp-deploy@${PROJECT_ID}.iam.gserviceaccount.com"
for role in roles/run.admin roles/cloudbuild.builds.editor \
            roles/artifactregistry.writer roles/iam.serviceAccountUser \
            roles/storage.admin; do
  gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:${DEPLOY_SA}" --role="$role" --condition=None
done

# Pool + proveedor OIDC de GitHub
gcloud iam workload-identity-pools create github --project="$PROJECT_ID" \
  --location=global --display-name="GitHub"
gcloud iam workload-identity-pools providers create-oidc github \
  --project="$PROJECT_ID" --location=global \
  --workload-identity-pool=github --display-name="GitHub OIDC" \
  --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository" \
  --attribute-condition="assertion.repository=='${REPO}'" \
  --issuer-uri="https://token.actions.githubusercontent.com"

# Permitir que el repo impersone la SA
gcloud iam service-accounts add-iam-policy-binding "$DEPLOY_SA" \
  --project="$PROJECT_ID" --role=roles/iam.workloadIdentityUser \
  --member="principalSet://iam.googleapis.com/projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/github/attribute.repository/${REPO}"

# El valor para el secret GCP_WORKLOAD_IDENTITY_PROVIDER:
echo "projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/github/providers/github"
```

### Deploy manual con Cloud Build (sin GitHub)

```bash
gcloud builds submit --config infra/cloudrun/cloudbuild.yaml \
  --substitutions=_REGION=us-central1,_TAG=$(git rev-parse --short HEAD)
```

## Limpieza

```bash
source infra/cloudrun/.env
gcloud run services delete "$API_SERVICE" --region "$REGION"
gcloud run services delete "$WEB_SERVICE" --region "$REGION"
gcloud sql instances delete "$DB_INSTANCE"
gcloud artifacts repositories delete "$AR_REPO" --location "$REGION"
```
