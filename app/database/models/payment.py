from __future__ import annotations
import enum
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import Enum, ForeignKey, Integer, Numeric, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.session import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .order import Order


class PaymentStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    method: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    status: Mapped[PaymentStatus] = mapped_column(Enum(PaymentStatus), nullable=False)

    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id"), nullable=False, unique=True
    )
    order: Mapped["Order"] = relationship("Order", back_populates="payment")
