from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from app.database.session import Base


class ProductImage(Base):
    __tablename__ = "product_images"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    image_url = Column(String, nullable=False)
    is_main = Column(Boolean, default=False)
