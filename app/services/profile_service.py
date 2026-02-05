from exceptiongroup import catch
from pymysql import IntegrityError
from sqlalchemy.orm import Session

from app.database.models.profile import Profile
from app.schemas.profile import ProfileCreate
import logging

logger = logging.getLogger(__name__)


class ProfileService:

    @staticmethod
    def create(db: Session, profile_data: ProfileCreate):
        new_profile = Profile(**profile_data.model_dump())
        try:
            db.add(new_profile)
            db.commit()
            db.refresh(new_profile)
            return new_profile
        except IntegrityError as e:
            logger.error("DATABASE ERRROR", e)

    @staticmethod
    def update(db: Session, id: int, profile_data: ProfileCreate):
        profile_db = db.get(Profile, id)
        if not profile_db:
            raise ValueError("Profile doesn't exits")

        update_profile = profile_data.model_dump(exclude_unset=True)
        for key, value in update_profile.items():
            setattr(profile_db, key, value)
        try:
            db.commit()
            db.refresh(profile_db)
            return profile_db
        except IntegrityError as e:
            logger.error("DATABASE ERRROR", e)
