from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import Usuario


class MetodoDePago(Base):
    __tablename__ = "metodos_de_pago"

    id: Mapped[int] = mapped_column(primary_key=True)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    tipo: Mapped[str] = mapped_column(String(50))
    detalles: Mapped[str] = mapped_column(String(255))

    cliente: Mapped[Usuario] = relationship(back_populates="metodos_de_pago")
