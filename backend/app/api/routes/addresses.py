from fastapi import APIRouter, HTTPException, status

from app.core.deps import CurrentUser, DbSession
from app.models.address import Direccion
from app.schemas.address import DireccionCreate, DireccionRead

router = APIRouter()


@router.get("", response_model=list[DireccionRead])
def list_direcciones(current_user: CurrentUser, db: DbSession) -> list[Direccion]:
    """Direcciones del usuario autenticado."""
    return (
        db.query(Direccion)
        .filter(Direccion.cliente_id == current_user.id)
        .all()
    )


@router.post("", response_model=DireccionRead, status_code=status.HTTP_201_CREATED)
def create_direccion(
    payload: DireccionCreate,
    current_user: CurrentUser,
    db: DbSession,
) -> Direccion:
    direccion = Direccion(cliente_id=current_user.id, **payload.model_dump())
    db.add(direccion)
    db.commit()
    db.refresh(direccion)
    return direccion


@router.delete("/{direccion_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_direccion(
    direccion_id: int,
    current_user: CurrentUser,
    db: DbSession,
) -> None:
    direccion = db.get(Direccion, direccion_id)
    if direccion is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dirección no encontrada",
        )
    if direccion.cliente_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Esa dirección no es tuya",
        )
    db.delete(direccion)
    db.commit()
