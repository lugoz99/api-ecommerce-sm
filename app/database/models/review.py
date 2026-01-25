from pymysql import Date
from sqlalchemy import Column, Integer, String
from app.database.session import Base
from datetime import datetime, timezone


class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True)
    comment = Column(String(255), nullable=False)
    review_date = Column(Date)
    rating = Column(Integer, default=lambda: datetime.now(timezone.utc))
