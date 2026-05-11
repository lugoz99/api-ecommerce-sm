from sqlalchemy.orm import Session
from app.database.models.category import Category
from app.exceptions.custom_exceptions import ConflictException, NotFoundException
from app.schemas.category import CategoryCreate
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
    def bulk_create(db: Session, categories_schema: list[CategoryCreate]):
        try:
            # 1. Obtener todos los nombres que vienen
            names = [c.name for c in categories_schema]

            # 2. Traer los nombres que ya existen (1 sola query)
            existing = (
                db.execute(select(Category.name).where(Category.name.in_(names)))
                .scalars()
                .all()
            )

            existing_set = set(existing)

            # 3. Filtrar solo los nuevos
            new_data = [
                c.model_dump() for c in categories_schema if c.name not in existing_set
            ]

            # 4. Insertar en bloque
            if new_data:
                db.execute(insert(Category), new_data)

            db.commit()
            return new_data

        except Exception:
            db.rollback()
            raise

    @staticmethod
    def exist_by_name(db: Session, name: str) -> bool:
        stmt = select(exists().where(Category.name == name))
        return db.scalar(stmt)

    @staticmethod
    def delete(db: Session, id: int) -> bool:
        categoryDb = db.get(Category, id)
        if not categoryDb:
            raise NotFoundException("Category not found")
        db.delete(categoryDb)
        db.commit()
