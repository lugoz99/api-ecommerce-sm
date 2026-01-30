from app.schemas.custom_base import CustomBase


class CategoryCreate(CustomBase):
    name: str
    category_id: int


class CategoryResponse(CustomBase):
    id: int
    name: str
