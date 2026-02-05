from annotated_types import Ge
from app.schemas.custom_base import CustomBase
from enum import Enum


class Gender(str, Enum):
    male = "male"
    female = "female"
    other = "other"
    prefer_not_to_say = "prefer_not_to_say"


class ProfileCreate(CustomBase):
    country: str
    date_birth: str
    photo: str
    gender: Gender


class ProfileResponse(CustomBase):
    country: str
    date_birth: str
    photo: str
    gender: str
