from fastapi.testclient import TestClient

from app.models.category import Categoria
from tests.conftest import login_headers, registrar


def _setup_servicio(client: TestClient, db) -> tuple[dict, int, int]:
    """Crea categoría + profesional con un servicio y un calendario.

    Devuelve (headers_pro, servicio_id, calendario_id).
    """
    cat = Categoria(nombre="Hogar")
    db.add(cat)
    db.commit()
    db.refresh(cat)

    registrar(client, "pro@example.com")
    headers = login_headers(client, "pro@example.com")
    serv = client.post(
        "/api/v1/servicios", headers=headers, json={"main_category": cat.id}
    ).json()
    cal = client.post("/api/v1/calendarios", headers=headers, json={}).json()
    return headers, serv["id"], cal["id"]


def _payload(servicio_id: int, cal_id: int) -> dict:
    return {
        "servicio_id": servicio_id,
        "calendario_id": cal_id,
        "fecha_contratacion": "2026-06-20",
        "hora_contratacion": "11:00:00",
        "contacto": "11-1234-5678",
        "domicilio": "Calle Falsa 123",
    }


def test_cliente_contrata_servicio(client: TestClient, db):
    _, serv_id, cal_id = _setup_servicio(client, db)
    registrar(client, "cliente@example.com")
    h_cli = login_headers(client, "cliente@example.com")

    resp = client.post(
        "/api/v1/contrataciones", headers=h_cli, json=_payload(serv_id, cal_id)
    )
    assert resp.status_code == 201, resp.text
    assert resp.json()["estado"] == "pendiente"
    assert resp.json()["servicio"]["id"] == serv_id


def test_no_se_puede_contratar_servicio_propio(client: TestClient, db):
    h_pro, serv_id, cal_id = _setup_servicio(client, db)
    resp = client.post(
        "/api/v1/contrataciones", headers=h_pro, json=_payload(serv_id, cal_id)
    )
    assert resp.status_code == 400


def test_listado_por_rol_y_cambio_de_estado(client: TestClient, db):
    h_pro, serv_id, cal_id = _setup_servicio(client, db)
    registrar(client, "cliente@example.com")
    h_cli = login_headers(client, "cliente@example.com")
    cont = client.post(
        "/api/v1/contrataciones", headers=h_cli, json=_payload(serv_id, cal_id)
    ).json()

    # El cliente la ve como cliente
    como_cliente = client.get(
        "/api/v1/contrataciones", headers=h_cli, params={"rol": "cliente"}
    )
    assert len(como_cliente.json()) == 1

    # El profesional la ve como profesional
    como_pro = client.get(
        "/api/v1/contrataciones", headers=h_pro, params={"rol": "profesional"}
    )
    assert len(como_pro.json()) == 1

    # El cliente NO puede cambiar el estado
    bloqueado = client.patch(
        f"/api/v1/contrataciones/{cont['id']}",
        headers=h_cli,
        json={"estado": "aceptada"},
    )
    assert bloqueado.status_code == 403

    # El profesional sí
    ok = client.patch(
        f"/api/v1/contrataciones/{cont['id']}",
        headers=h_pro,
        json={"estado": "aceptada"},
    )
    assert ok.status_code == 200
    assert ok.json()["estado"] == "aceptada"
