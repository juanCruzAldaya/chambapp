from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.service import Servicio
    from app.models.user import Usuario


class Resena(Base):
    __tablename__ = "resenas"

    id: Mapped[int] = mapped_column(primary_key=True)
    servicio_id: Mapped[int] = mapped_column(ForeignKey("servicios.id"))
    cliente_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    calificacion: Mapped[int] = mapped_column()  # 1..5 (validado en el schema)
    comentario: Mapped[str | None] = mapped_column(Text)
    fecha: Mapped[date] = mapped_column(server_default=func.current_date())

    servicio: Mapped[Servicio] = relationship(back_populates="resenas")
    cliente: Mapped[Usuario] = relationship(back_populates="resenas")
