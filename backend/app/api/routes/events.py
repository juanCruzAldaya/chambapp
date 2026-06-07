from fastapi import APIRouter, HTTPException, status

from app.core.deps import CurrentUser, DbSession
from app.models.calendar import Calendario
from app.models.event import Evento
from app.schemas.event import EventoCreate, EventoRead, EventoUpdate

router = APIRouter()


def _calendario_propio_o_error(
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


def _get_evento_o_404(db: DbSession, evento_id: int) -> Evento:
    evento = db.get(Evento, evento_id)
    if evento is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento no encontrado",
        )
    return evento


@router.get("", response_model=list[EventoRead])
def list_eventos(calendario_id: int, db: DbSession) -> list[Evento]:
    """Slots de un calendario (disponibilidad pública)."""
    if db.get(Calendario, calendario_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calendario no encontrado",
        )
    return (
        db.query(Evento)
        .filter(Evento.calendario_id == calendario_id)
        .order_by(Evento.fecha, Evento.hora_inicio)
        .all()
    )


@router.post("", response_model=EventoRead, status_code=status.HTTP_201_CREATED)
def create_evento(
    payload: EventoCreate,
    current_user: CurrentUser,
    db: DbSession,
) -> Evento:
    """Crea un slot de disponibilidad en un calendario propio."""
    _calendario_propio_o_error(db, payload.calendario_id, current_user.id)
    evento = Evento(**payload.model_dump())
    db.add(evento)
    db.commit()
    db.refresh(evento)
    return evento


@router.patch("/{evento_id}", response_model=EventoRead)
def update_evento(
    evento_id: int,
    payload: EventoUpdate,
    current_user: CurrentUser,
    db: DbSession,
) -> Evento:
    evento = _get_evento_o_404(db, evento_id)
    _calendario_propio_o_error(db, evento.calendario_id, current_user.id)

    datos = payload.model_dump(exclude_unset=True)
    hora_inicio = datos.get("hora_inicio", evento.hora_inicio)
    hora_fin = datos.get("hora_fin", evento.hora_fin)
    if hora_fin <= hora_inicio:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="hora_fin debe ser posterior a hora_inicio",
        )
    for campo, valor in datos.items():
        setattr(evento, campo, valor)
    db.commit()
    db.refresh(evento)
    return evento


@router.delete("/{evento_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_evento(
    evento_id: int,
    current_user: CurrentUser,
    db: DbSession,
) -> None:
    evento = _get_evento_o_404(db, evento_id)
    _calendario_propio_o_error(db, evento.calendario_id, current_user.id)
    db.delete(evento)
    db.commit()
