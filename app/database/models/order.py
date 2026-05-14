from __future__ import annotations

import enum
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import Enum, ForeignKey, Integer, Numeric, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.models.payment import PaymentStatus
from app.database.session import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .payment import Payment
    from .order_detail import OrderDetail
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
    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, default=Decimal("0.00")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus), default=OrderStatus.pending, nullable=False
    )

    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), nullable=False)
    customer: Mapped["Customer"] = relationship("Customer", back_populates="orders")

    order_details: Mapped[list["OrderDetail"]] = relationship(
        "OrderDetail", back_populates="order", cascade="all, delete-orphan"
    )
    payment: Mapped["Payment"] = relationship(
        "Payment", back_populates="order", uselist=False, cascade="all, delete-orphan"
    )

    @property
    def is_paid(self) -> bool:
        return (
            self.payment is not None and self.payment.status == PaymentStatus.completed
        )

    def calculate_total(self) -> Decimal:
        """Calcula el total desde los detalles de la orden"""
        return sum(detail.quantity * detail.price for detail in self.order_details)

    def update_total(self) -> None:
        """Actualiza el total_amount basado en order_details"""
        self.total_amount = self.calculate_total()
