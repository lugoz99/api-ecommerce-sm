from __future__ import annotations

from typing import TYPE_CHECKING
from datetime import datetime, date
from sqlalchemy import Date, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, validates, relationship

from app.database.session import Base

if TYPE_CHECKING:
    from .product import Product


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True)

    comment: Mapped[str] = mapped_column(nullable=False)

    # Fecha del día automáticamente (sin hora)
    review_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        server_default=func.current_date(),
    )

    # Rating entre 1 y 5
    rating: Mapped[int] = mapped_column(nullable=False)

    # Fecha y hora de creación automática
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    # Many to one , mucho va la foreing key
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    # back_popultaes -> Sincroniza ambos lados de una relación bidireccional
    product: Mapped["Product"] = relationship()

    # Validación del rango de rating
    @validates("rating")
    def check_rating(self, key, value):
        if value < 1 or value > 5:
            raise ValueError("rating must be between 1 and 5")
        return value
