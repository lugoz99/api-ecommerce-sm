from __future__ import annotations

import enum
from datetime import datetime, timezone
import black
from sqlalchemy import Enum, ForeignKey, Integer, Numeric, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.session import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .payment import Payment
    from .customer import Customer


class OrderStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    total_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus), default=OrderStatus.pending, nullable=False
    )

    payments: Mapped[list["Payment"]] = relationship(
        "Payment", cascade="all, delete-orphan"
    )

    customer_id: Mapped[int] = ForeignKey("customers.id")
    customer: Mapped["Customer"] = relationship("Customer", back_populates="orders")
