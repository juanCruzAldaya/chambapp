from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.category import Categoria, SubCategoria
    from app.models.contract import Contratacion
    from app.models.review import Resena
    from app.models.user import Usuario


class Servicio(Base):
    __tablename__ = "servicios"

    id: Mapped[int] = mapped_column(primary_key=True)
    profesional_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    description: Mapped[str | None] = mapped_column(Text)
    main_category: Mapped[int] = mapped_column(ForeignKey("categorias.id"))
    secondary_category: Mapped[int | None] = mapped_column(
        ForeignKey("subcategorias.id")
    )
    state: Mapped[str | None] = mapped_column(String(100))
    department: Mapped[str | None] = mapped_column(String(100))
    locality: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    profesional: Mapped[Usuario] = relationship(
        back_populates="servicios", foreign_keys=[profesional_id]
    )
    categoria_principal: Mapped[Categoria] = relationship(
        back_populates="servicios", foreign_keys=[main_category]
    )
    subcategoria: Mapped[SubCategoria | None] = relationship(
        foreign_keys=[secondary_category]
    )
    contrataciones: Mapped[list[Contratacion]] = relationship(
        back_populates="servicio", cascade="all, delete-orphan"
    )
    resenas: Mapped[list[Resena]] = relationship(
        back_populates="servicio", cascade="all, delete-orphan"
    )
