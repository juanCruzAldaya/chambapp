from fastapi.testclient import TestClient

from app.models.category import Categoria
from tests.conftest import login_headers, registrar


def _crear_categoria(db) -> int:
    cat = Categoria(nombre="Hogar")
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat.id


def test_crear_servicio_requiere_auth(client: TestClient):
    resp = client.post("/api/v1/servicios", json={"main_category": 1})
    assert resp.status_code == 401


def test_crear_y_buscar_servicio(client: TestClient, db):
    cat_id = _crear_categoria(db)
    registrar(client, "pro@example.com")
    headers = login_headers(client, "pro@example.com")

    resp = client.post(
        "/api/v1/servicios",
        headers=headers,
        json={
            "main_category": cat_id,
            "description": "Arreglo canillas y caños",
            "locality": "Centro",
        },
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["categoria_principal"]["nombre"] == "Hogar"
    assert body["profesional"]["nombre"] == "pro"

    # Búsqueda por texto
    encontrados = client.get("/api/v1/servicios", params={"q": "canillas"})
    assert encontrados.status_code == 200
    assert len(encontrados.json()) == 1

    # Filtro que no matchea
    vacio = client.get("/api/v1/servicios", params={"q": "inexistente"})
    assert vacio.json() == []


def test_categoria_inexistente_da_404(client: TestClient):
    registrar(client, "pro@example.com")
    headers = login_headers(client, "pro@example.com")
    resp = client.post(
        "/api/v1/servicios", headers=headers, json={"main_category": 999}
    )
    assert resp.status_code == 404


def test_update_servicio_solo_dueno(client: TestClient, db):
    cat_id = _crear_categoria(db)
    registrar(client, "dueno@example.com")
    headers_dueno = login_headers(client, "dueno@example.com")
    serv = client.post(
        "/api/v1/servicios",
        headers=headers_dueno,
        json={"main_category": cat_id, "description": "original"},
    ).json()

    registrar(client, "otro@example.com")
    headers_otro = login_headers(client, "otro@example.com")
    resp = client.patch(
        f"/api/v1/servicios/{serv['id']}",
        headers=headers_otro,
        json={"description": "hackeado"},
    )
    assert resp.status_code == 403

    ok = client.patch(
        f"/api/v1/servicios/{serv['id']}",
        headers=headers_dueno,
        json={"description": "actualizado"},
    )
    assert ok.status_code == 200
    assert ok.json()["description"] == "actualizado"


def test_delete_servicio(client: TestClient, db):
    cat_id = _crear_categoria(db)
    registrar(client, "del@example.com")
    headers = login_headers(client, "del@example.com")
    serv = client.post(
        "/api/v1/servicios", headers=headers, json={"main_category": cat_id}
    ).json()

    resp = client.delete(f"/api/v1/servicios/{serv['id']}", headers=headers)
    assert resp.status_code == 204
    assert client.get(f"/api/v1/servicios/{serv['id']}").status_code == 404
