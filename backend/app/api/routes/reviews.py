from decimal import Decimal

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import func

from app.core.deps import CurrentUser, DbSession
from app.models.review import Resena
from app.models.service import Servicio
from app.models.user import Usuario
from app.schemas.review import ResenaCreate, ResenaRead

router = APIRouter()


def _recalcular_promedio_profesional(db: DbSession, profesional_id: int) -> None:
    """Recalcula el promedio de calificaciones de todos los servicios del profesional."""
    promedio = (
        db.query(func.avg(Resena.calificacion))
        .join(Servicio, Resena.servicio_id == Servicio.id)
        .filter(Servicio.profesional_id == profesional_id)
        .scalar()
    )
    profesional = db.get(Usuario, profesional_id)
    if profesional is not None:
        profesional.calificacion_promedio = (
            Decimal(promedio).quantize(Decimal("0.01"))
            if promedio is not None
            else None
        )


@router.get("", response_model=list[ResenaRead])
def list_resenas(servicio_id: int, db: DbSession) -> list[Resena]:
    """Reseñas de un servicio."""
    if db.get(Servicio, servicio_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Servicio no encontrado",
        )
    return (
        db.query(Resena)
        .filter(Resena.servicio_id == servicio_id)
        .order_by(Resena.fecha.desc())
        .all()
    )


@router.post("", response_model=ResenaRead, status_code=status.HTTP_201_CREATED)
def create_resena(
    payload: ResenaCreate,
    current_user: CurrentUser,
    db: DbSession,
) -> Resena:
    """Deja una reseña sobre un servicio y actualiza el promedio del profesional."""
    servicio = db.get(Servicio, payload.servicio_id)
    if servicio is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El servicio no existe",
        )
    if servicio.profesional_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No podés reseñar tu propio servicio",
        )

    resena = Resena(
        servicio_id=payload.servicio_id,
        cliente_id=current_user.id,
        calificacion=payload.calificacion,
        comentario=payload.comentario,
    )
    db.add(resena)
    db.flush()  # persiste la reseña antes de recalcular el promedio
    _recalcular_promedio_profesional(db, servicio.profesional_id)
    db.commit()
    db.refresh(resena)
    return resena
