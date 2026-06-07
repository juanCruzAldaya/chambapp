from typing import Annotated, Literal

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy.orm import joinedload

from app.core.deps import CurrentUser, DbSession
from app.models.calendar import Calendario
from app.models.contract import Contratacion
from app.models.event import Evento
from app.models.service import Servicio
from app.schemas.contract import (
    ContratacionCreate,
    ContratacionRead,
    ContratacionUpdate,
)

router = APIRouter()


def _get_contratacion_o_404(db: DbSession, contratacion_id: int) -> Contratacion:
    contratacion = (
        db.query(Contratacion)
        .options(joinedload(Contratacion.servicio))
        .filter(Contratacion.id == contratacion_id)
        .first()
    )
    if contratacion is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contratación no encontrada",
        )
    return contratacion


@router.get("", response_model=list[ContratacionRead])
def list_mis_contrataciones(
    current_user: CurrentUser,
    db: DbSession,
    rol: Annotated[
        Literal["cliente", "profesional"],
        Query(description="Ver como cliente (contraté) o profesional (me contrataron)"),
    ] = "cliente",
) -> list[Contratacion]:
    """Contrataciones del usuario, según el rol elegido."""
    query = db.query(Contratacion).options(joinedload(Contratacion.servicio))
    if rol == "cliente":
        query = query.filter(Contratacion.cliente_id == current_user.id)
    else:
        query = query.join(Servicio).filter(
            Servicio.profesional_id == current_user.id
        )
    return query.order_by(Contratacion.fecha_contratacion.desc()).all()


@router.post("", response_model=ContratacionRead, status_code=status.HTTP_201_CREATED)
def create_contratacion(
    payload: ContratacionCreate,
    current_user: CurrentUser,
    db: DbSession,
) -> Contratacion:
    """Contrata un servicio. El usuario autenticado es el cliente."""
    servicio = db.get(Servicio, payload.servicio_id)
    if servicio is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El servicio no existe",
        )
    if servicio.profesional_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No podés contratar tu propio servicio",
        )
    if db.get(Calendario, payload.calendario_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El calendario no existe",
        )
    if payload.evento_id is not None and db.get(Evento, payload.evento_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El evento no existe",
        )

    contratacion = Contratacion(cliente_id=current_user.id, **payload.model_dump())
    db.add(contratacion)
    db.commit()
    db.refresh(contratacion)
    return contratacion


@router.get("/{contratacion_id}", response_model=ContratacionRead)
def get_contratacion(
    contratacion_id: int,
    current_user: CurrentUser,
    db: DbSession,
) -> Contratacion:
    contratacion = _get_contratacion_o_404(db, contratacion_id)
    es_cliente = contratacion.cliente_id == current_user.id
    es_profesional = contratacion.servicio.profesional_id == current_user.id
    if not (es_cliente or es_profesional):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tenés acceso a esta contratación",
        )
    return contratacion


@router.patch("/{contratacion_id}", response_model=ContratacionRead)
def update_contratacion(
    contratacion_id: int,
    payload: ContratacionUpdate,
    current_user: CurrentUser,
    db: DbSession,
) -> Contratacion:
    """El profesional cambia el estado; el cliente edita comentarios."""
    contratacion = _get_contratacion_o_404(db, contratacion_id)
    es_cliente = contratacion.cliente_id == current_user.id
    es_profesional = contratacion.servicio.profesional_id == current_user.id
    if not (es_cliente or es_profesional):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tenés acceso a esta contratación",
        )

    datos = payload.model_dump(exclude_unset=True)
    if "estado" in datos and not es_profesional:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el profesional puede cambiar el estado",
        )
    for campo, valor in datos.items():
        setattr(contratacion, campo, valor)
    db.commit()
    db.refresh(contratacion)
    return contratacion
