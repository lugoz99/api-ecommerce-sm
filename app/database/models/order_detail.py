from __future__ import annotations
import enum
from datetime import datetime, timezone
from sqlalchemy import Integer, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.session import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .order import Order
    from .product import Product


class OrderDetail(Base):
    __tablename__ = "order_details"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
