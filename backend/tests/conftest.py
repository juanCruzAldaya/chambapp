"""Fixtures de pytest: base SQLite en memoria + cliente con auth.

La DB usa StaticPool sobre `sqlite://` (memoria) para que todas las sesiones
compartan la misma conexión. Se recrea el esquema en cada test (aislamiento).
"""

import os

# Debe setearse antes de importar la app: evita que el lifespan intente
# crear tablas contra Postgres (solo lo hace en ENVIRONMENT=local).
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("DATABASE_URL", "sqlite://")

from collections.abc import Generator  # noqa: E402

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import Session, sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from app.core.database import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db() -> Generator[Session, None, None]:
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ─── Helpers de autenticación ────────────────────────────────

def registrar(client: TestClient, email: str, password: str = "password123") -> dict:
    resp = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "nombre": email.split("@")[0]},
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def login_headers(client: TestClient, email: str, password: str = "password123") -> dict:
    resp = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
    )
    assert resp.status_code == 200, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_client(client: TestClient) -> tuple[TestClient, dict, dict]:
    """Cliente con un usuario registrado y logueado. Devuelve (client, headers, user)."""
    user = registrar(client, "pro@example.com")
    headers = login_headers(client, "pro@example.com")
    return client, headers, user
