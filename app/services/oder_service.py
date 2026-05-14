
from sqlalchemy.orm import Session

from app.database.models.order import Order
from app.schemas.order import OrderCreate


class OrderService:
  
  @staticmethod
  def create(db: Session, order_data: OrderCreate) -> Order:
    pass