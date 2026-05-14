from idna import intranges_contain
from pydantic import field_validator
from app.schemas.category import CategoryResponse
from app.schemas.custom_base import CustomBase
from app.utils.normalizer import normalize_text


class ProductCreate(CustomBase):
    name: str
    price: float
    quantity: int
    brand: str
    description: str
    tags: dict | None
    category_id: int

    @field_validator("name")
    @classmethod
    def clean_name(cls, v):
        return normalize_text(v)

    @field_validator("brand")
    @classmethod
    def clean_brand(cls, v):
        return normalize_text(v)


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


class ReviewCreate(CustomBase):
    rating: int
    comment: str


class ProductImageResponse(CustomBase):
    id: int
    url: str
    product_id: int
    cloud_id: str
    is_main: bool
