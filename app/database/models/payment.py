from pymysql import Date
from sqlalchemy import Column, Enum, Integer, Numeric, String
from app.database.session import Base
import enum
from datetime import datetime, timezone


class Status(enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"
    cancelled = "failed"


class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True)
    total_amount = Column(Numeric(10, 2), nullable=False)
    method = Column(String(100), nullable=False)
    created_at = Column(Date, lambda: datetime.now(timezone.utc))
    status = Column(Enum(Status))
