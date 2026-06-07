from fastapi.testclient import TestClient

from tests.conftest import login_headers, registrar


def test_register_y_perfil_no_devuelve_password(client: TestClient):
    user = registrar(client, "nuevo@example.com")
    assert user["email"] == "nuevo@example.com"
    assert "password" not in user
    assert user["id"] > 0


def test_register_email_duplicado(client: TestClient):
    registrar(client, "dup@example.com")
    resp = client.post(
        "/api/v1/auth/register",
        json={"email": "dup@example.com", "password": "password123"},
    )
    assert resp.status_code == 409


def test_register_password_corta(client: TestClient):
    resp = client.post(
        "/api/v1/auth/register",
        json={"email": "corta@example.com", "password": "123"},
    )
    assert resp.status_code == 422


def test_login_ok_y_credenciales_invalidas(client: TestClient):
    registrar(client, "login@example.com")
    headers = login_headers(client, "login@example.com")
    assert headers["Authorization"].startswith("Bearer ")

    mala = client.post(
        "/api/v1/auth/login",
        data={"username": "login@example.com", "password": "incorrecta"},
    )
    assert mala.status_code == 401


def test_me_requiere_token(client: TestClient):
    assert client.get("/api/v1/usuarios/me").status_code == 401


def test_me_con_token(client: TestClient):
    registrar(client, "me@example.com")
    headers = login_headers(client, "me@example.com")
    resp = client.get("/api/v1/usuarios/me", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["email"] == "me@example.com"
