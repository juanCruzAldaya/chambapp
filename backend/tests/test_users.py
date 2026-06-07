from fastapi.testclient import TestClient

from tests.conftest import login_headers, registrar


def test_update_me(client: TestClient):
    registrar(client, "edit@example.com")
    headers = login_headers(client, "edit@example.com")
    resp = client.patch(
        "/api/v1/usuarios/me",
        headers=headers,
        json={"nombre": "Juan", "ciudad": "Rosario"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["nombre"] == "Juan"
    assert body["ciudad"] == "Rosario"


def test_get_usuario_publico(client: TestClient):
    user = registrar(client, "publico@example.com")
    resp = client.get(f"/api/v1/usuarios/{user['id']}")
    assert resp.status_code == 200
    assert resp.json()["email"] == "publico@example.com"
    assert "password" not in resp.json()


def test_get_usuario_inexistente(client: TestClient):
    assert client.get("/api/v1/usuarios/9999").status_code == 404
