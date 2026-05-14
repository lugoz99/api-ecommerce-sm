from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal
from typing import Optional
from app.database.models.order import OrderStatus


class OrderCreate(BaseModel):
    customer_id: int
    order_details_ids: list[int]  # Array de IDs de order_details
    status: Optional[OrderStatus] = OrderStatus.pending


class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    order_details_ids: Optional[list[int]] = None


class OrderResponse(BaseModel):
    id: int
    customer_id: int
    total_amount: Decimal
    status: OrderStatus
    created_at: datetime
    updated_at: datetime
    order_details_ids: list[int]  # Array con IDs de order_details

    class Config:
        from_attributes = True
