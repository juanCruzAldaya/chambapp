from fastapi import APIRouter, HTTPException, status
from sqlalchemy.orm import selectinload

from app.core.deps import CurrentUser, DbSession
from app.models.calendar import Calendario
from app.schemas.calendar import (
    CalendarioConEventos,
    CalendarioCreate,
    CalendarioRead,
)

router = APIRouter()


def _get_calendario_propio_o_404(
    db: DbSession, calendario_id: int, usuario_id: int
) -> Calendario:
    calendario = db.get(Calendario, calendario_id)
    if calendario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calendario no encontrado",
        )
    if calendario.usuario_id != usuario_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ese calendario no es tuyo",
        )
    return calendario


@router.get("", response_model=list[CalendarioRead])
def list_mis_calendarios(current_user: CurrentUser, db: DbSession) -> list[Calendario]:
    """Calendarios del usuario autenticado."""
    return (
        db.query(Calendario)
        .filter(Calendario.usuario_id == current_user.id)
        .order_by(Calendario.anio, Calendario.mes)
        .all()
    )


@router.post("", response_model=CalendarioRead, status_code=status.HTTP_201_CREATED)
def create_calendario(
    payload: CalendarioCreate,
    current_user: CurrentUser,
    db: DbSession,
) -> Calendario:
    calendario = Calendario(usuario_id=current_user.id, **payload.model_dump())
    db.add(calendario)
    db.commit()
    db.refresh(calendario)
    return calendario


@router.get("/{calendario_id}", response_model=CalendarioConEventos)
def get_calendario(calendario_id: int, db: DbSession) -> Calendario:
    """Detalle de un calendario con sus eventos (disponibilidad pública)."""
    calendario = (
        db.query(Calendario)
        .options(selectinload(Calendario.eventos))
        .filter(Calendario.id == calendario_id)
        .first()
    )
    if calendario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calendario no encontrado",
        )
    return calendario


@router.delete("/{calendario_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_calendario(
    calendario_id: int,
    current_user: CurrentUser,
    db: DbSession,
) -> None:
    calendario = _get_calendario_propio_o_404(db, calendario_id, current_user.id)
    db.delete(calendario)
    db.commit()
