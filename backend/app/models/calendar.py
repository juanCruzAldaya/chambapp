from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.event import Evento
    from app.models.user import Usuario


class Calendario(Base):
    __tablename__ = "calendarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    anio: Mapped[int | None] = mapped_column()
    mes: Mapped[int | None] = mapped_column()

    usuario: Mapped[Usuario] = relationship(back_populates="calendarios")
    eventos: Mapped[list[Evento]] = relationship(
        back_populates="calendario", cascade="all, delete-orphan"
    )
