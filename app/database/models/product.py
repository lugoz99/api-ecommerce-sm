from __future__ import annotations

from typing import TYPE_CHECKING, Any
from datetime import datetime

from sqlalchemy import (
    JSON,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Numeric,
    func,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.database.session import Base

# TYPE_CHECKING evita imports circulares en tiempo de ejecución
if TYPE_CHECKING:
    from .category import Category
    from .product_image import ProductImage


class Product(Base):
    """
    Modelo de productos.

    Incluye:
    - Información básica
    - Relación con categorías
    - Relación con imágenes
    - Fechas automáticas
    """

    __tablename__ = "products"

    # =========================================================
    # PRIMARY KEY
    # =========================================================
    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    # =========================================================
    # CAMPOS BÁSICOS
    # =========================================================

    # Nombre del producto
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    # Precio
    #
    # Numeric(10,2):
    # hasta 10 dígitos
    # 2 decimales
    #
    price: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    # Stock disponible
    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    # Marca
    brand: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    # Descripción
    description: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # =========================================================
    # TAGS DINÁMICOS
    # =========================================================
    #
    # JSON permite guardar datos flexibles:
    #
    # {
    #   "color": "red",
    #   "storage": "256GB"
    # }
    #
    tags: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=True,
    )

    # =========================================================
    # FECHAS AUTOMÁTICAS
    # =========================================================

    # Fecha de creación
    #
    # server_default=func.now():
    # El DEFAULT se genera directamente en MySQL.
    #
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # Fecha de actualización
    #
    # onupdate=func.now():
    # Se actualiza automáticamente en UPDATE.
    #
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # =========================================================
    # FOREIGN KEY
    # =========================================================

    # Relación con categoría
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id"),
        nullable=False,
        index=True,
    )

    # =========================================================
    # RELACIÓN MANY-TO-ONE
    # =========================================================
    #
    # Muchos productos pertenecen a una categoría.
    #
    category: Mapped["Category"] = relationship(
        "Category",
        back_populates="products",
    )

    # =========================================================
    # RELACIÓN ONE-TO-MANY
    # =========================================================
    #
    # Un producto puede tener muchas imágenes.
    #
    # cascade="all, delete-orphan":
    #
    # Si borras el producto:
    # - se borran sus imágenes automáticamente.
    #
    images: Mapped[list["ProductImage"]] = relationship(
        "ProductImage",
        back_populates="product",
        cascade="all, delete-orphan",
    )

    # =========================================================
    # REPRESENTACIÓN
    # =========================================================
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id}, name={self.name})"