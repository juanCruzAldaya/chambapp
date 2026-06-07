from fastapi import APIRouter, HTTPException, status

from app.core.deps import CurrentUser, DbSession
from app.models.user import Usuario
from app.schemas.user import UsuarioRead, UsuarioUpdate

router = APIRouter()


@router.get("/me", response_model=UsuarioRead)
def get_me(current_user: CurrentUser) -> Usuario:
    """Perfil del usuario autenticado."""
    return current_user


@router.patch("/me", response_model=UsuarioRead)
def update_me(
    payload: UsuarioUpdate,
    current_user: CurrentUser,
    db: DbSession,
) -> Usuario:
    """Actualiza parcialmente el perfil propio."""
    datos = payload.model_dump(exclude_unset=True)
    for campo, valor in datos.items():
        setattr(current_user, campo, valor)
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/{usuario_id}", response_model=UsuarioRead)
def get_usuario(usuario_id: int, db: DbSession) -> Usuario:
    """Perfil público de cualquier usuario (sin password)."""
    usuario = db.get(Usuario, usuario_id)
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )
    return usuario
