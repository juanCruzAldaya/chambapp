from fastapi.testclient import TestClient

from app.db.seed import seed_categorias
from tests.conftest import login_headers, registrar


def test_crear_categoria_requiere_auth(client: TestClient):
    resp = client.post("/api/v1/categorias", json={"nombre": "Plomería"})
    assert resp.status_code == 401


def test_crear_listar_categoria_y_subcategoria(client: TestClient):
    registrar(client, "cat@example.com")
    headers = login_headers(client, "cat@example.com")

    cat = client.post("/api/v1/categorias", json={"nombre": "Hogar"}, headers=headers)
    assert cat.status_code == 201
    cat_id = cat.json()["id"]

    dup = client.post("/api/v1/categorias", json={"nombre": "Hogar"}, headers=headers)
    assert dup.status_code == 409

    sub = client.post(
        f"/api/v1/categorias/{cat_id}/subcategorias",
        json={"nombre": "Plomería"},
        headers=headers,
    )
    assert sub.status_code == 201

    listado = client.get("/api/v1/categorias")
    assert listado.status_code == 200
    data = listado.json()
    assert len(data) == 1
    assert data[0]["subcategorias"][0]["nombre"] == "Plomería"


def test_seed_es_idempotente(client: TestClient, db):
    cats1, subs1 = seed_categorias(db)
    assert cats1 > 0 and subs1 > 0
    cats2, subs2 = seed_categorias(db)
    assert cats2 == 0 and subs2 == 0

    listado = client.get("/api/v1/categorias")
    assert len(listado.json()) == cats1
