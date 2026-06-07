from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class ResenaCreate(BaseModel):
    servicio_id: int
    calificacion: int = Field(ge=1, le=5)
    comentario: str | None = None


class ResenaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    servicio_id: int
    cliente_id: int
    calificacion: int
    comentario: str | None = None
    fecha: date
