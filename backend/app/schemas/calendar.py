from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.event import EventoRead


class CalendarioCreate(BaseModel):
    anio: int | None = Field(default=None, ge=2000, le=2100)
    mes: int | None = Field(default=None, ge=1, le=12)


class CalendarioRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    usuario_id: int
    anio: int | None = None
    mes: int | None = None


class CalendarioConEventos(CalendarioRead):
    eventos: list[EventoRead] = []
