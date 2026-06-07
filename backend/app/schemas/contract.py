from __future__ import annotations

from datetime import date, time

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.service import ServicioRead


class ContratacionCreate(BaseModel):
    servicio_id: int
    calendario_id: int
    evento_id: int | None = None
    fecha_contratacion: date
    hora_contratacion: time
    contacto: str = Field(min_length=1, max_length=100)
    domicilio: str = Field(min_length=1, max_length=255)
    comentarios: str | None = None


class ContratacionUpdate(BaseModel):
    """El profesional actualiza el estado; el cliente puede dejar comentarios."""

    estado: str | None = Field(default=None, max_length=50)
    comentarios: str | None = None


class ContratacionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cliente_id: int
    servicio_id: int
    calendario_id: int
    evento_id: int | None = None
    fecha_contratacion: date
    hora_contratacion: time
    contacto: str
    domicilio: str
    estado: str
    comentarios: str | None = None
    servicio: ServicioRead | None = None
