from __future__ import annotations

from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base

if TYPE_CHECKING:
    from .product import Product


class ProductImage(Base):
    __tablename__ = "product_images"

    id: Mapped[int] = mapped_column(primary_key=True)

    url: Mapped[str] = mapped_column(String(255), nullable=False)

    cloud_id: Mapped[str] = mapped_column(String(255), nullable=False)

    # Many-to-One: ProductImage -> Product
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))

    product: Mapped["Product"] = relationship(
        "Product",
        back_populates="images",
    )

    # Indica si esta imagen es la principal del producto
    is_main: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
