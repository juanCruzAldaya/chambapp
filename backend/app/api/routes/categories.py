from fastapi import APIRouter, HTTPException, status
from sqlalchemy.orm import selectinload

from app.core.deps import CurrentUser, DbSession
from app.models.category import Categoria, SubCategoria
from app.schemas.category import (
    CategoriaConSubcategorias,
    CategoriaCreate,
    CategoriaRead,
    SubCategoriaCreate,
    SubCategoriaRead,
)

router = APIRouter()


@router.get("", response_model=list[CategoriaConSubcategorias])
def list_categorias(db: DbSession) -> list[Categoria]:
    """Árbol completo de categorías con sus subcategorías."""
    return (
        db.query(Categoria)
        .options(selectinload(Categoria.subcategorias))
        .order_by(Categoria.nombre)
        .all()
    )


@router.post(
    "",
    response_model=CategoriaRead,
    status_code=status.HTTP_201_CREATED,
)
def create_categoria(
    payload: CategoriaCreate,
    db: DbSession,
    _: CurrentUser,
) -> Categoria:
    """Crea una categoría (requiere autenticación). El nombre es único."""
    existe = db.query(Categoria).filter(Categoria.nombre == payload.nombre).first()
    if existe:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una categoría con ese nombre",
        )
    categoria = Categoria(nombre=payload.nombre)
    db.add(categoria)
    db.commit()
    db.refresh(categoria)
    return categoria


@router.get("/{categoria_id}", response_model=CategoriaConSubcategorias)
def get_categoria(categoria_id: int, db: DbSession) -> Categoria:
    categoria = db.get(Categoria, categoria_id)
    if categoria is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoría no encontrada",
        )
    return categoria


@router.get(
    "/{categoria_id}/subcategorias",
    response_model=list[SubCategoriaRead],
)
def list_subcategorias(categoria_id: int, db: DbSession) -> list[SubCategoria]:
    categoria = db.get(Categoria, categoria_id)
    if categoria is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoría no encontrada",
        )
    return (
        db.query(SubCategoria)
        .filter(SubCategoria.categoria_id == categoria_id)
        .order_by(SubCategoria.nombre)
        .all()
    )


@router.post(
    "/{categoria_id}/subcategorias",
    response_model=SubCategoriaRead,
    status_code=status.HTTP_201_CREATED,
)
def create_subcategoria(
    categoria_id: int,
    payload: SubCategoriaCreate,
    db: DbSession,
    _: CurrentUser,
) -> SubCategoria:
    categoria = db.get(Categoria, categoria_id)
    if categoria is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoría no encontrada",
        )
    subcategoria = SubCategoria(nombre=payload.nombre, categoria_id=categoria_id)
    db.add(subcategoria)
    db.commit()
    db.refresh(subcategoria)
    return subcategoria
