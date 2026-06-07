from fastapi.testclient import TestClient

from tests.conftest import login_headers, registrar


def _auth(client: TestClient, email: str) -> dict:
    registrar(client, email)
    return login_headers(client, email)


def test_crear_calendario_y_evento(client: TestClient):
    headers = _auth(client, "agenda@example.com")

    cal = client.post(
        "/api/v1/calendarios", headers=headers, json={"anio": 2026, "mes": 6}
    )
    assert cal.status_code == 201
    cal_id = cal.json()["id"]

    ev = client.post(
        "/api/v1/eventos",
        headers=headers,
        json={
            "calendario_id": cal_id,
            "fecha": "2026-06-15",
            "hora_inicio": "09:00:00",
            "hora_fin": "10:00:00",
        },
    )
    assert ev.status_code == 201, ev.text
    assert ev.json()["estado"] == "disponible"

    # Detalle del calendario incluye el evento
    detalle = client.get(f"/api/v1/calendarios/{cal_id}")
    assert len(detalle.json()["eventos"]) == 1

    # Listado de eventos por calendario
    eventos = client.get("/api/v1/eventos", params={"calendario_id": cal_id})
    assert len(eventos.json()) == 1


def test_evento_rango_horario_invalido(client: TestClient):
    headers = _auth(client, "rango@example.com")
    cal_id = client.post("/api/v1/calendarios", headers=headers, json={}).json()["id"]
    resp = client.post(
        "/api/v1/eventos",
        headers=headers,
        json={
            "calendario_id": cal_id,
            "fecha": "2026-06-15",
            "hora_inicio": "10:00:00",
            "hora_fin": "09:00:00",
        },
    )
    assert resp.status_code == 422


def test_evento_en_calendario_ajeno_prohibido(client: TestClient):
    headers_a = _auth(client, "duenoa@example.com")
    cal_id = client.post(
        "/api/v1/calendarios", headers=headers_a, json={}
    ).json()["id"]

    headers_b = _auth(client, "intruso@example.com")
    resp = client.post(
        "/api/v1/eventos",
        headers=headers_b,
        json={
            "calendario_id": cal_id,
            "fecha": "2026-06-15",
            "hora_inicio": "09:00:00",
            "hora_fin": "10:00:00",
        },
    )
    assert resp.status_code == 403
