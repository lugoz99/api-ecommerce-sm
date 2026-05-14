from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models.review import Review
from app.schemas.product import ReviewCreate


class ReviewServce:

    @staticmethod
    def create(db: Session, review_data: ReviewCreate):
        try:
            review_data = ReviewCreate(**review_data.model_dump())
            review = Review(**review_data.model_dump())
            db.add(review)
            db.commit()
            db.refresh(review)
            return review
        except Exception as e:
            raise ValueError("Invalid review data") from e

    @staticmethod
    def get(db: Session, rating: int = None):
        # TODO: ADD FILTERS
        query = select(Review)
        if rating is not None:
            query = query.where(Review.rating == rating)
        return db.scalars(query).all()
