from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.database.models.category import Category
from app.exceptions.custom_exceptions import ConflictException, NotFoundException
from app.schemas.category import BulkCategoryResponse, CategoryCreate, CategoryUpdate
from sqlalchemy import exists, insert, select


class CategoryService:

    @staticmethod
    def get(db: Session) -> list[Category]:
        return db.execute(select(Category)).scalars().all()

    @staticmethod
    def create(db: Session, category_schema: CategoryCreate):
        if CategoryService.exist_by_name(db, category_schema.name):
            raise ConflictException("The product already existS!")
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
    def get_by_id(db: Session, category_id: int) -> Category | None:
        try:
            category_db = db.get(Category, category_id)
            if category_db is None:
                raise NotFoundException("Category not found")
            return category_db
        except SQLAlchemyError:
            db.rollback()
            raise

    @staticmethod
    def update(db: Session, category_update: CategoryUpdate) -> Category:
        category_db = db.get(Category, category_update.id)
        if category_db is None:
            raise NotFoundException("Category not found")
        if CategoryService.exist_by_name(db, category_update.name):
            raise ConflictException("The category already existS!")
        try:
            category_db.name = category_update.name
            db.commit()
            db.refresh(category_db)
            return category_db
        except SQLAlchemyError:
            db.rollback()
            raise

    @staticmethod
    def delete(db: Session, category_id: int) -> None:
        category_db = db.get(Category, category_id)
        if category_db is None:
            raise NotFoundException("Category not found")
        try:
            db.delete(category_db)
            db.commit()
        except SQLAlchemyError:
            db.rollback()
            raise

    @staticmethod
    def bulk_create(
        db: Session, categories_schema: list[CategoryCreate]
    ) -> BulkCategoryResponse:
        try:
            # Obtener todos los nombres enviados
            names = [category.name for category in categories_schema]

            # Consultar cuáles ya existen en DB
            existing = (
                db.execute(select(Category.name).where(Category.name.in_(names)))
                .scalars()
                .all()
            )

            # Convertir a set para búsqueda rápida O(1)
            existing_set = set(existing)
            created_categories = []
            already_exists = []

            for category in categories_schema:
                if category.name in existing_set:
                    already_exists.append(category.name)
                else:
                    created_categories.append(Category(**category.model_dump()))

            if created_categories:
                db.add_all(created_categories)
                db.commit()
                # Refrescar para obtener ids y defaults
                for category in created_categories:
                    db.refresh(category)

            # Retornar resultado detallado
            return BulkCategoryResponse(
                created=created_categories,
                already_exists=already_exists,
            )

        except SQLAlchemyError:
            # Revertir transacción en caso de error
            db.rollback()
            raise
