from app.schemas.category import CategoryResponse
from app.schemas.custom_base import CustomBase


class ProductCreate(CustomBase):
    name: str
    price: float
    quantity: int
    brand: str
    description: str
    tags: dict | None
    category_id: int


class ProductResponse(CustomBase):
    id: int
    name: str
    price: float
    quantity: int
    brand: str
    description: str
    tags: dict | None
    category_id: int
    category: CategoryResponse


class ProductUpdate(CustomBase):
    id: int
    name: str
    price: float
    quantity: int
    brand: str
    description: str
    tags: dict | None
    category_id: int
