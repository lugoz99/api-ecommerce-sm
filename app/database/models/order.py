from pymysql import Date
from sqlalchemy import Column, Enum, Integer, Numeric
from app.database.session import Base
import enum
from datetime import datetime, timezone


class Status(enum.Enum):
    pending = "pending"
    processing = "processing"
    shipped = "shipped"
    delivered = "delivered"
    canceled = "cancelled"


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    total_amount = Column(Numeric(10, 2), nullable=False)
    created_at = Column(Date, lambda: datetime.now(timezone.utc))
    status = Column(Enum(Status), default=Status.pending)
