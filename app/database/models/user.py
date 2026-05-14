from ntpath import realpath
from typing import TYPE_CHECKING
from sqlalchemy.orm import relationship

from app.database.session import Base
from sqlalchemy import Column, Integer, String, Boolean

if TYPE_CHECKING:
    from .profile import Profile


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    # userList -> retrun a unique profile for each user (1-a-1)
    profile = relationship("Profile", uselist=False)
