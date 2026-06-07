# ─── Build (Node) ────────────────────────────────────────────
FROM node:22-alpine AS build

WORKDIR /app

# Instala dependencias con el lockfile (capa cacheable)
COPY package.json package-lock.json ./
RUN npm ci

COPY . .

# URL de la API horneada en el bundle (Vite lee VITE_* de .env.production).
# Se pasa como build-arg al construir la imagen, ej:
#   --build-arg VITE_API_URL=https://chambapp-api-xxxx.run.app/api/v1
ARG VITE_API_URL=/api/v1
RUN echo "VITE_API_URL=${VITE_API_URL}" > .env.production
RUN npm run build

# ─── Runtime (nginx) ─────────────────────────────────────────
FROM nginx:1.27-alpine AS runtime

# El entrypoint oficial de nginx hace envsubst de los *.template
# (sustituye ${PORT} que inyecta Cloud Run) y los escribe en conf.d/.
COPY nginx.conf.template /etc/nginx/templates/default.conf.template
COPY --from=build /app/dist /usr/share/nginx/html

# Cloud Run inyecta $PORT; default 8080.
ENV PORT=8080
EXPOSE 8080
