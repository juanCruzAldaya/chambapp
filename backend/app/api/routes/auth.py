from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.deps import DbSession
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import Usuario
from app.schemas.token import Token
from app.schemas.user import UsuarioCreate, UsuarioRead

router = APIRouter()


@router.post(
    "/register",
    response_model=UsuarioRead,
    status_code=status.HTTP_201_CREATED,
)
def register(payload: UsuarioCreate, db: DbSession) -> Usuario:
    """Registra un nuevo usuario. El email debe ser único."""
    existe = db.query(Usuario).filter(Usuario.email == payload.email).first()
    if existe:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un usuario con ese email",
        )

    usuario = Usuario(
        email=payload.email,
        password=hash_password(payload.password),
        nombre=payload.nombre,
        apellido=payload.apellido,
        contacto=payload.contacto,
        ciudad=payload.ciudad,
        nacimiento=payload.nacimiento,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


@router.post("/login", response_model=Token)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: DbSession,
) -> Token:
    """Login OAuth2 password flow. El `username` del form es el email."""
    usuario = db.query(Usuario).filter(Usuario.email == form_data.username).first()
    if usuario is None or not verify_password(form_data.password, usuario.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(subject=usuario.email)
    return Token(access_token=token)
