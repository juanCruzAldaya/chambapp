from __future__ import annotations

from datetime import date, time

from pydantic import BaseModel, ConfigDict, Field, model_validator


class EventoBase(BaseModel):
    fecha: date
    hora_inicio: time
    hora_fin: time
    estado: str = Field(default="disponible", max_length=50)

    @model_validator(mode="after")
    def validar_rango_horario(self) -> EventoBase:
        if self.hora_fin <= self.hora_inicio:
            raise ValueError("hora_fin debe ser posterior a hora_inicio")
        return self


class EventoCreate(EventoBase):
    calendario_id: int


class EventoUpdate(BaseModel):
    fecha: date | None = None
    hora_inicio: time | None = None
    hora_fin: time | None = None
    estado: str | None = Field(default=None, max_length=50)


class EventoRead(EventoBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    calendario_id: int
