from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import Usuario


class Direccion(Base):
    __tablename__ = "direcciones"

    id: Mapped[int] = mapped_column(primary_key=True)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    direccion: Mapped[str] = mapped_column(String(255))
    ciudad: Mapped[str] = mapped_column(String(100))
    codigo_postal: Mapped[str] = mapped_column(String(20))

    cliente: Mapped[Usuario] = relationship(back_populates="direcciones")
