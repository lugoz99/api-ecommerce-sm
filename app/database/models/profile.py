from sqlalchemy import Column, Enum, Integer, String
from app.database.session import Base
import enum


class Gender(enum.Enum):
    male = "male"
    female = "female"
    other = "other"
    prefer_not_to_say = "prefer_not_to_say"


class Profile(Base):
    __tablename__ = "profiles"
    id = Column(Integer, primary_key=True)
    country = Column(String(100))
    date_birth = Column(String(100))
    photo = Column(String(255))
    gender = Column(Enum(Gender), default=Gender.prefer_not_to_say)
