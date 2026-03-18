from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models.review import Review
from app.schemas.product import ReviewCreate


class ReviewServce:

    @staticmethod
    def create(db: Session, review_data: ReviewCreate):
        review = Review(**review_data.model_dump())
        db.add(review)
        db.commit()
        db.refresh(review)
        return review

    @staticmethod
    def get(db: Session):
        # TODO: ADD FILTERS
        return db.scalars(select(Review)).all()
