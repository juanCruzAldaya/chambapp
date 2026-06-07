from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.service import Servicio


class Categoria(Base):
    __tablename__ = "categorias"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), unique=True)

    subcategorias: Mapped[list[SubCategoria]] = relationship(
        back_populates="categoria", cascade="all, delete-orphan"
    )
    servicios: Mapped[list[Servicio]] = relationship(
        back_populates="categoria_principal",
        foreign_keys="Servicio.main_category",
    )


class SubCategoria(Base):
    __tablename__ = "subcategorias"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100))
    categoria_id: Mapped[int] = mapped_column(ForeignKey("categorias.id"))

    categoria: Mapped[Categoria] = relationship(back_populates="subcategorias")
