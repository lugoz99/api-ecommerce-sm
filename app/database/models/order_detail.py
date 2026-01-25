from pymysql import Date
from sqlalchemy import Column, Integer, Numeric
from app.database.session import Base
from datetime import datetime, timezone


class OrderDetail(Base):
    __tablename__ = "order_details"
    id = Column(Integer, primary_key=True)
    quantity = Column(Integer, nullable=False)
    created_at = Column(Date, lambda: datetime.now(timezone.utc))
    price = Column(Numeric(10, 2), nullable=False)
