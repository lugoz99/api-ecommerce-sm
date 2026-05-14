from pydantic import field_validator

from app.schemas.custom_base import CustomBase
from app.utils.normalizer import normalize_text


class CategoryCreate(CustomBase):
    name: str

    @field_validator("name")
    @classmethod
    def clean_name(cls, v):
        return normalize_text(v)


class CategoryResponse(CustomBase):
    id: int
    name: str


class CategoryUpdate(CustomBase):
    id: int
    name: str


class BulkCategoryResponse(CustomBase):
    created: list[CategoryResponse]
    already_exists: list[str]
