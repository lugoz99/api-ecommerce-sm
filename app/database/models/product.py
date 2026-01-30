from __future__ import annotations

from typing import TYPE_CHECKING, Any
from datetime import datetime
from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base

if TYPE_CHECKING:
    from .category import Category
    from .product_image import ProductImage


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    brand: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(255))
    tags: Mapped[dict[str, Any]] = mapped_column(JSON)
    # Fechas automáticas
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    # Relación inversa con Category
    category: Mapped["Category"] = relationship(
        "Category",
        back_populates="products",
    )

    # One-to-Many: Product -> ProductImage
    # Si borras un Product → se borran sus imágenes
    images: Mapped[list["ProductImage"]] = relationship(
        "ProductImage",
        back_populates="product",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name})"
