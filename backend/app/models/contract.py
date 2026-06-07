from __future__ import annotations

from datetime import date, time
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.service import Servicio
    from app.models.user import Usuario


class Contratacion(Base):
    __tablename__ = "contrataciones"

    id: Mapped[int] = mapped_column(primary_key=True)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    servicio_id: Mapped[int] = mapped_column(ForeignKey("servicios.id"))
    fecha_contratacion: Mapped[date] = mapped_column()
    hora_contratacion: Mapped[time] = mapped_column()
    calendario_id: Mapped[int] = mapped_column(ForeignKey("calendarios.id"))
    evento_id: Mapped[int | None] = mapped_column(ForeignKey("eventos.id"))
    contacto: Mapped[str] = mapped_column(String(100))
    domicilio: Mapped[str] = mapped_column(String(255))
    estado: Mapped[str] = mapped_column(String(50), default="pendiente")
    comentarios: Mapped[str | None] = mapped_column(Text)

    cliente: Mapped[Usuario] = relationship(back_populates="contrataciones")
    servicio: Mapped[Servicio] = relationship(back_populates="contrataciones")
