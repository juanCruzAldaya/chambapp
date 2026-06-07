from fastapi import APIRouter, HTTPException, status

from app.core.deps import CurrentUser, DbSession
from app.models.payment_method import MetodoDePago
from app.schemas.payment_method import MetodoDePagoCreate, MetodoDePagoRead

router = APIRouter()


@router.get("", response_model=list[MetodoDePagoRead])
def list_metodos(current_user: CurrentUser, db: DbSession) -> list[MetodoDePago]:
    """Métodos de pago del usuario autenticado."""
    return (
        db.query(MetodoDePago)
        .filter(MetodoDePago.cliente_id == current_user.id)
        .all()
    )


@router.post("", response_model=MetodoDePagoRead, status_code=status.HTTP_201_CREATED)
def create_metodo(
    payload: MetodoDePagoCreate,
    current_user: CurrentUser,
    db: DbSession,
) -> MetodoDePago:
    metodo = MetodoDePago(cliente_id=current_user.id, **payload.model_dump())
    db.add(metodo)
    db.commit()
    db.refresh(metodo)
    return metodo


@router.delete("/{metodo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_metodo(
    metodo_id: int,
    current_user: CurrentUser,
    db: DbSession,
) -> None:
    metodo = db.get(MetodoDePago, metodo_id)
    if metodo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Método de pago no encontrado",
        )
    if metodo.cliente_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ese método de pago no es tuyo",
        )
    db.delete(metodo)
    db.commit()
