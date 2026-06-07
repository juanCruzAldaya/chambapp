from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.address import Direccion
    from app.models.calendar import Calendario
    from app.models.contract import Contratacion
    from app.models.payment_method import MetodoDePago
    from app.models.review import Resena
    from app.models.service import Servicio


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password: Mapped[str] = mapped_column(String(255))  # hash bcrypt
    nombre: Mapped[str | None] = mapped_column(String(100))
    apellido: Mapped[str | None] = mapped_column(String(100))
    contacto: Mapped[str | None] = mapped_column(String(100))
    ciudad: Mapped[str | None] = mapped_column(String(100))
    nacimiento: Mapped[date | None] = mapped_column()
    calificacion_promedio: Mapped[Decimal | None] = mapped_column(Numeric(3, 2))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Como profesional
    servicios: Mapped[list[Servicio]] = relationship(
        back_populates="profesional",
        foreign_keys="Servicio.profesional_id",
        cascade="all, delete-orphan",
    )
    calendarios: Mapped[list[Calendario]] = relationship(
        back_populates="usuario", cascade="all, delete-orphan"
    )

    # Como cliente
    contrataciones: Mapped[list[Contratacion]] = relationship(
        back_populates="cliente", cascade="all, delete-orphan"
    )
    resenas: Mapped[list[Resena]] = relationship(
        back_populates="cliente", cascade="all, delete-orphan"
    )
    metodos_de_pago: Mapped[list[MetodoDePago]] = relationship(
        back_populates="cliente", cascade="all, delete-orphan"
    )
    direcciones: Mapped[list[Direccion]] = relationship(
        back_populates="cliente", cascade="all, delete-orphan"
    )
