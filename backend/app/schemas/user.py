from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UsuarioBase(BaseModel):
    """Campos editables de perfil, compartidos entre create y update."""

    nombre: str | None = Field(default=None, max_length=100)
    apellido: str | None = Field(default=None, max_length=100)
    contacto: str | None = Field(default=None, max_length=100)
    ciudad: str | None = Field(default=None, max_length=100)
    nacimiento: date | None = None


class UsuarioCreate(UsuarioBase):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UsuarioUpdate(UsuarioBase):
    """Todos los campos opcionales: PATCH parcial del propio perfil."""


class UsuarioRead(UsuarioBase):
    """Perfil público / propio. Nunca incluye el password."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    calificacion_promedio: Decimal | None = None
    created_at: datetime
