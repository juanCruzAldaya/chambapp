from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy.orm import joinedload

from app.core.deps import CurrentUser, DbSession
from app.models.category import Categoria, SubCategoria
from app.models.service import Servicio
from app.schemas.service import ServicioCreate, ServicioRead, ServicioUpdate

router = APIRouter()


def _validar_categorias(
    db: DbSession,
    main_category: int | None,
    secondary_category: int | None,
) -> None:
    """Verifica que la categoría principal y la sub (si viene) existan."""
    if main_category is not None and db.get(Categoria, main_category) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La categoría principal no existe",
        )
    if (
        secondary_category is not None
        and db.get(SubCategoria, secondary_category) is None
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La subcategoría no existe",
        )


def _get_servicio_o_404(db: DbSession, servicio_id: int) -> Servicio:
    servicio = db.get(Servicio, servicio_id)
    if servicio is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Servicio no encontrado",
        )
    return servicio


@router.get("", response_model=list[ServicioRead])
def search_servicios(
    db: DbSession,
    q: Annotated[str | None, Query(description="Texto en la descripción")] = None,
    main_category: int | None = None,
    secondary_category: int | None = None,
    state: str | None = None,
    department: str | None = None,
    locality: str | None = None,
    profesional_id: int | None = None,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> list[Servicio]:
    """Búsqueda de servicios con filtros opcionales y paginación."""
    query = db.query(Servicio).options(
        joinedload(Servicio.categoria_principal),
        joinedload(Servicio.subcategoria),
        joinedload(Servicio.profesional),
    )
    if q:
        query = query.filter(Servicio.description.ilike(f"%{q}%"))
    if main_category is not None:
        query = query.filter(Servicio.main_category == main_category)
    if secondary_category is not None:
        query = query.filter(Servicio.secondary_category == secondary_category)
    if state:
        query = query.filter(Servicio.state == state)
    if department:
        query = query.filter(Servicio.department == department)
    if locality:
        query = query.filter(Servicio.locality == locality)
    if profesional_id is not None:
        query = query.filter(Servicio.profesional_id == profesional_id)

    return (
        query.order_by(Servicio.created_at.desc()).offset(skip).limit(limit).all()
    )


@router.post("", response_model=ServicioRead, status_code=status.HTTP_201_CREATED)
def create_servicio(
    payload: ServicioCreate,
    current_user: CurrentUser,
    db: DbSession,
) -> Servicio:
    """Publica un servicio. El usuario autenticado es el profesional."""
    _validar_categorias(db, payload.main_category, payload.secondary_category)
    servicio = Servicio(
        profesional_id=current_user.id,
        **payload.model_dump(),
    )
    db.add(servicio)
    db.commit()
    db.refresh(servicio)
    return servicio


@router.get("/{servicio_id}", response_model=ServicioRead)
def get_servicio(servicio_id: int, db: DbSession) -> Servicio:
    return _get_servicio_o_404(db, servicio_id)


@router.patch("/{servicio_id}", response_model=ServicioRead)
def update_servicio(
    servicio_id: int,
    payload: ServicioUpdate,
    current_user: CurrentUser,
    db: DbSession,
) -> Servicio:
    """Actualiza un servicio. Solo el profesional dueño puede hacerlo."""
    servicio = _get_servicio_o_404(db, servicio_id)
    if servicio.profesional_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No podés modificar un servicio que no es tuyo",
        )
    datos = payload.model_dump(exclude_unset=True)
    if "main_category" in datos or "secondary_category" in datos:
        _validar_categorias(
            db,
            datos.get("main_category"),
            datos.get("secondary_category"),
        )
    for campo, valor in datos.items():
        setattr(servicio, campo, valor)
    db.commit()
    db.refresh(servicio)
    return servicio


@router.delete("/{servicio_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_servicio(
    servicio_id: int,
    current_user: CurrentUser,
    db: DbSession,
) -> None:
    servicio = _get_servicio_o_404(db, servicio_id)
    if servicio.profesional_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No podés eliminar un servicio que no es tuyo",
        )
    db.delete(servicio)
    db.commit()
