# ─── Base ────────────────────────────────────────────────────
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    ENVIRONMENT=production

WORKDIR /app

# Dependencias del sistema mínimas (psycopg2 ya viene como binary wheel)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .
RUN chmod +x entrypoint.sh

# Usuario sin privilegios
RUN useradd --create-home --uid 1000 appuser
USER appuser

# Cloud Run inyecta $PORT; por defecto 8080
ENV PORT=8080
EXPOSE 8080

ENTRYPOINT ["./entrypoint.sh"]
