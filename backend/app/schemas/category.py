from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class SubCategoriaCreate(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)


class SubCategoriaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    categoria_id: int


class CategoriaCreate(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)


class CategoriaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str


class CategoriaConSubcategorias(CategoriaRead):
    """Categoría con sus subcategorías embebidas (para el árbol de navegación)."""

    subcategorias: list[SubCategoriaRead] = []
