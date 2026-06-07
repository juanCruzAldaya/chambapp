from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class MetodoDePagoCreate(BaseModel):
    tipo: str = Field(min_length=1, max_length=50)
    detalles: str = Field(min_length=1, max_length=255)


class MetodoDePagoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cliente_id: int
    tipo: str
    detalles: str
