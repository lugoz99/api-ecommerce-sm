from __future__ import annotations

from sqlalchemy import String
from app.database.session import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from .order import Order


class Customer(Base):
    __tablename__ = "customers"
    id: Mapped[int] = mapped_column(primary_key=True)
    names: Mapped[str] = mapped_column(String(100), nullable=False)
    last_names: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(100), nullable=False)
    address: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at = mapped_column(default=lambda: datetime.now(timezone.utc))
    orders: Mapped[list["Order"]] = relationship("Order", back_populates="customer")
