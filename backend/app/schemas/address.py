from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class DireccionCreate(BaseModel):
    direccion: str = Field(min_length=1, max_length=255)
    ciudad: str = Field(min_length=1, max_length=100)
    codigo_postal: str = Field(min_length=1, max_length=20)


class DireccionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cliente_id: int
    direccion: str
    ciudad: str
    codigo_postal: str
