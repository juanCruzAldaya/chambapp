from __future__ import annotations

from datetime import date, time
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.calendar import Calendario


class Evento(Base):
    __tablename__ = "eventos"

    id: Mapped[int] = mapped_column(primary_key=True)
    calendario_id: Mapped[int] = mapped_column(ForeignKey("calendarios.id"))
    fecha: Mapped[date] = mapped_column()
    hora_inicio: Mapped[time] = mapped_column()
    hora_fin: Mapped[time] = mapped_column()
    estado: Mapped[str] = mapped_column(String(50), default="disponible")

    calendario: Mapped[Calendario] = relationship(back_populates="eventos")
