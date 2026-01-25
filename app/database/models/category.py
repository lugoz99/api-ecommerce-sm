from sqlalchemy import Column, Integer, String, true
from app.database.session import Base


class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True)
    name = Column(String)
