from app.schemas.custom_base import CustomBase


class CategoryCreate(CustomBase):
    name: str


class CategoryResponse(CustomBase):
    id: int
    name: str
