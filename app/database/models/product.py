from __future__ import annotations

from typing import TYPE_CHECKING
from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Numeric
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
    tags: Mapped[dict] = mapped_column(JSON)

    created_at: Mapped[DateTime] = mapped_column(DateTime)
    updated_at: Mapped[DateTime] = mapped_column(DateTime)

    # Many-to-One: Product -> Category
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))

    category: Mapped["Category"] = relationship("Category", back_populates="products")

    # One-to-Many: Product -> ProductImage
    # Si borras una Category → se borran sus Product

    # Si quitas un Product de category.products → se borra de la BD

    # Evita productos “huérfanos
    images: Mapped[list["ProductImage"]] = relationship(
        "ProductImage", back_populates="product", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name})"
