from sqlalchemy import Column, Integer, String
from app.database.session import Base


class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True)
    names = Column(String(100), nullable=False)
    last_names = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    phone_number = Column(String(100), nullable=False)
    address = Column(String(100), nullable=False)
