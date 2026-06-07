# GKE — Kubernetes (Fase 5, estudio)

Misma app que en Cloud Run, pero orquestada con **Kubernetes** en **GKE
Autopilot**. Es la fase de aprendizaje: ver cómo se traduce todo a Deployments,
Services, Ingress, HPA, Secrets y Workload Identity.

> ⚠️ **Costo**: GKE **no tiene free tier** útil. Cluster + Cloud SQL + Load
> Balancer del Ingress cuestan plata mientras estén prendidos (~USD 50–100+/mes).
> Para sólo estudiar, leé los manifests; no hace falta desplegar. Si desplegás,
> **acordate de borrar todo** (ver "Limpieza").

## Arquitectura

```
                          Ingress (GCE HTTP LB)
                          /api/*  ┌───────────────┐
   internet ───────────►─────────┤ Service api    ├─► Pods chambapp-api ─┐
                          /*      └───────────────┘   (api + proxy SQL)  │
                                  ┌───────────────┐                      ▼
                          ───────►┤ Service web    ├─► Pods chambapp-web  Cloud SQL
                                  └───────────────┘   (nginx SPA)       (Postgres)
```

- **Mismo origen**: el Ingress manda `/api/*` al backend y el resto al frontend,
  así que la SPA usa `VITE_API_URL=/api/v1` y **no hay CORS**.
- **Cloud SQL Auth Proxy** como *sidecar* en cada pod de la API: la app habla a
  `127.0.0.1:5432` y el proxy tuneliza a Cloud SQL, autenticándose por
  **Workload Identity** (sin claves).
- **Migraciones**: un `Job` corre `alembic upgrade head` (+ seed) una sola vez.
- **HPA**: autoescala por CPU.

## Manifests

| Archivo | Qué define |
|---------|-----------|
| `01-namespace.yaml`     | namespace `chambapp` |
| `02-serviceaccount.yaml`| KSA con anotación de Workload Identity |
| `03-secret.example.yaml`| ejemplo (el real lo crea `deploy.sh` con kubectl) |
| `04-backend.yaml`       | Deployment API + sidecar proxy + Service |
| `05-frontend.yaml`      | Deployment nginx + Service |
| `06-migrate-job.yaml`   | Job de migraciones (proxy como native sidecar) |
| `07-ingress.yaml`       | Ingress GCE con routing por path |
| `08-hpa.yaml`           | HorizontalPodAutoscaler de api y web |

Los `${VAR}` se resuelven con `envsubst` dentro de `deploy.sh`.

## Desplegar (si te animás al costo)

```bash
cd infra/k8s
cp .env.example .env      # completar PROJECT_ID
gcloud components install kubectl gke-gcloud-auth-plugin   # si no los tenés

./setup-cluster.sh        # cluster Autopilot + Cloud SQL + Workload Identity
./deploy.sh               # build imágenes + aplica manifests + migra

# Esperar la IP del Ingress (unos minutos):
kubectl -n chambapp get ingress chambapp -w
# Abrir http://<IP>/  (y la API en http://<IP>/api/v1/... , docs en /docs)
```

## Comandos útiles para estudiar

```bash
kubectl -n chambapp get pods                 # estado de los pods
kubectl -n chambapp get deploy,svc,ingress,hpa
kubectl -n chambapp logs deploy/chambapp-api -c api        # logs de la app
kubectl -n chambapp logs deploy/chambapp-api -c cloud-sql-proxy
kubectl -n chambapp describe ingress chambapp              # estado del LB
kubectl -n chambapp rollout restart deploy/chambapp-api    # redeploy
kubectl -n chambapp scale deploy/chambapp-web --replicas=3 # escalar a mano
```

## Limpieza (¡importante para no pagar de más!)

```bash
source .env
gcloud container clusters delete "$CLUSTER" --region "$REGION"
gcloud sql instances delete "$DB_INSTANCE"
# El Load Balancer del Ingress se borra al borrar el cluster, pero verificá
# que no queden forwarding-rules/backends huérfanos en la consola.
```

> El detalle conceptual completo (qué es cada objeto, para qué sirve, cómo se usa
> en entrevistas) está en el HTML de estudio: `docs/estudio/fase-5.html`.
