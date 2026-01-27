from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import Base


class ProductImage(Base):
    __tablename__ = "product_images"

    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(String(255), nullable=False)

    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))

    is_main: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
