from pydantic import BaseModel, EmailStr, field_validator

from app.utils.normalizer import normalize_text


class UserCreate(BaseModel):
    email: EmailStr
    name: str

    @field_validator("name")
    @classmethod
    def clean_name(cls, v):
        return normalize_text(v)


class UserRead(BaseModel):
    id: int
    email: EmailStr
    name: str
