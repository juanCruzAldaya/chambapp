from fastapi.testclient import TestClient

from tests.conftest import login_headers, registrar


def _auth(client: TestClient, email: str) -> dict:
    registrar(client, email)
    return login_headers(client, email)


def test_metodos_de_pago_crud(client: TestClient):
    headers = _auth(client, "pago@example.com")
    creado = client.post(
        "/api/v1/metodos-de-pago",
        headers=headers,
        json={"tipo": "tarjeta", "detalles": "Visa ****1234"},
    )
    assert creado.status_code == 201
    mid = creado.json()["id"]

    listado = client.get("/api/v1/metodos-de-pago", headers=headers)
    assert len(listado.json()) == 1

    assert client.delete(
        f"/api/v1/metodos-de-pago/{mid}", headers=headers
    ).status_code == 204
    assert client.get("/api/v1/metodos-de-pago", headers=headers).json() == []


def test_metodo_ajeno_no_se_puede_borrar(client: TestClient):
    h1 = _auth(client, "a@example.com")
    mid = client.post(
        "/api/v1/metodos-de-pago",
        headers=h1,
        json={"tipo": "efectivo", "detalles": "-"},
    ).json()["id"]

    h2 = _auth(client, "b@example.com")
    assert client.delete(
        f"/api/v1/metodos-de-pago/{mid}", headers=h2
    ).status_code == 403


def test_direcciones_crud(client: TestClient):
    headers = _auth(client, "dir@example.com")
    creada = client.post(
        "/api/v1/direcciones",
        headers=headers,
        json={
            "direccion": "Av. Siempreviva 742",
            "ciudad": "Rosario",
            "codigo_postal": "2000",
        },
    )
    assert creada.status_code == 201
    listado = client.get("/api/v1/direcciones", headers=headers)
    assert len(listado.json()) == 1
