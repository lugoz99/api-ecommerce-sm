from sqlalchemy import JSON, Column, DateTime, Integer, String, Numeric
from sqlalchemy.orm import relationship
from app.database.session import Base


class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)  # dinero
    quantity = Column(Integer, nullable=False)  # unidades
    brand = Column(String(100))
    description = Column(String(255))
    tags = Column(JSON)
    images = relationship("ProductImage")
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
