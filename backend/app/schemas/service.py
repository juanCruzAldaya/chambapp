from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.category import CategoriaRead, SubCategoriaRead


class ServicioBase(BaseModel):
    description: str | None = None
    state: str | None = Field(default=None, max_length=100)
    department: str | None = Field(default=None, max_length=100)
    locality: str | None = Field(default=None, max_length=100)


class ServicioCreate(ServicioBase):
    main_category: int
    secondary_category: int | None = None


class ServicioUpdate(BaseModel):
    """PATCH parcial: todo opcional."""

    description: str | None = None
    main_category: int | None = None
    secondary_category: int | None = None
    state: str | None = Field(default=None, max_length=100)
    department: str | None = Field(default=None, max_length=100)
    locality: str | None = Field(default=None, max_length=100)


class ProfesionalResumen(BaseModel):
    """Datos mínimos del profesional embebidos en el servicio."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str | None = None
    apellido: str | None = None
    calificacion_promedio: Decimal | None = None


class ServicioRead(ServicioBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    profesional_id: int
    main_category: int
    secondary_category: int | None = None
    created_at: datetime
    categoria_principal: CategoriaRead | None = None
    subcategoria: SubCategoriaRead | None = None
    profesional: ProfesionalResumen | None = None
