from fastapi.testclient import TestClient

from app.models.category import Categoria
from tests.conftest import login_headers, registrar


def _setup_servicio(client: TestClient, db) -> tuple[dict, int, int]:
    """Crea categoría + profesional con un servicio.

    Devuelve (headers_pro, servicio_id, profesional_id).
    """
    cat = Categoria(nombre="Hogar")
    db.add(cat)
    db.commit()
    db.refresh(cat)

    pro = registrar(client, "pro@example.com")
    headers = login_headers(client, "pro@example.com")
    serv = client.post(
        "/api/v1/servicios", headers=headers, json={"main_category": cat.id}
    ).json()
    return headers, serv["id"], pro["id"]


def test_resena_actualiza_promedio_profesional(client: TestClient, db):
    _, serv_id, pro_id = _setup_servicio(client, db)

    registrar(client, "c1@example.com")
    h1 = login_headers(client, "c1@example.com")
    registrar(client, "c2@example.com")
    h2 = login_headers(client, "c2@example.com")

    r1 = client.post(
        "/api/v1/resenas",
        headers=h1,
        json={"servicio_id": serv_id, "calificacion": 4, "comentario": "Bien"},
    )
    assert r1.status_code == 201, r1.text
    r2 = client.post(
        "/api/v1/resenas",
        headers=h2,
        json={"servicio_id": serv_id, "calificacion": 5},
    )
    assert r2.status_code == 201

    # Promedio (4+5)/2 = 4.50 en el perfil del profesional
    perfil = client.get(f"/api/v1/usuarios/{pro_id}").json()
    assert float(perfil["calificacion_promedio"]) == 4.5

    # Listado de reseñas del servicio
    listado = client.get("/api/v1/resenas", params={"servicio_id": serv_id})
    assert len(listado.json()) == 2


def test_no_se_puede_resenar_servicio_propio(client: TestClient, db):
    h_pro, serv_id, _ = _setup_servicio(client, db)
    resp = client.post(
        "/api/v1/resenas",
        headers=h_pro,
        json={"servicio_id": serv_id, "calificacion": 5},
    )
    assert resp.status_code == 400


def test_calificacion_fuera_de_rango(client: TestClient, db):
    _, serv_id, _ = _setup_servicio(client, db)
    registrar(client, "c@example.com")
    h = login_headers(client, "c@example.com")
    resp = client.post(
        "/api/v1/resenas",
        headers=h,
        json={"servicio_id": serv_id, "calificacion": 6},
    )
    assert resp.status_code == 422
