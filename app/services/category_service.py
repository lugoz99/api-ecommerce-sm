from sqlalchemy.orm import Session
from app.database.models.category import Category
from app.schemas.category import CategoryCreate
from sqlalchemy import exists, select, values


class CategoryService:
    @staticmethod
    def create(db: Session, category_schema: CategoryCreate):
        if CategoryService.exist_by_name(db, category_schema.name):
            raise ValueError("The product already existS!")
        try:
            new_category = Category(**category_schema.model_dump())
            db.add(new_category)
            db.commit()
            db.refresh(new_category)
            return new_category
        except Exception as e:
            db.rollback()
            raise e

    @staticmethod
    def exist_by_name(db: Session, name: str) -> bool:
        stmt = select(exists().where(Category.name == name))
        return db.scalar(stmt)

    @staticmethod
    def delete(db: Session, id: int) -> bool:
        categoryDb = db.get(Category, id)
        if not categoryDb:
            raise ValueError("Category not found")
        db.delete(categoryDb)
        db.commit()
