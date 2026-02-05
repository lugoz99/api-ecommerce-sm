import logging
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.database.models.category import Category
from app.database.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate

logger = logging.getLogger(__name__)


class ProductService:

    @staticmethod
    def create(db: Session, product_data: ProductCreate) -> Product:
        category_exists = db.get(Category, product_data.category_id)
        if not category_exists:
            raise ValueError(
                f"Category with ID {product_data.category_id} does not exist"
            )
        product = Product(**product_data.model_dump())
        db.add(product)
        try:
            db.commit()
            db.refresh(product)
            return product
        except IntegrityError as e:
            db.rollback()
            # Detalle técnico para el developer en consola
            logger.error(f"DATABASE INTEGRITY ERROR (CREATE): {str(e.orig)}")
            raise ValueError("Create failed due to database integrity error")

    @staticmethod
    def get_all(db: Session) -> list[Product]:
        # * scalars convierte el result en objeto itereable | scalar es para solo devolver on campo
        return db.scalars(select(Product)).all()

    @staticmethod
    def get(db: Session, product_id: int) -> Product | None:
        return db.get(Product, product_id)

    @staticmethod
    def update(db: Session, product_id: int, product: ProductUpdate) -> Product | None:
        db_product = db.get(Product, product_id)
        if not db_product:
            raise ValueError("Product not found")
        category_exists = db.get(Category, product.category_id)
        if not category_exists:
            raise ValueError(f"Category with ID {product.category_id} does not exist")
        update_product = product.model_dump(exclude_unset=True)
        for field, value in update_product.items():
            setattr(db_product, field, value)
        try:
            db.commit()
            db.refresh(db_product)
            return db_product
        except IntegrityError as e:
            db.rollback()
            error_details = str(e.orig)
            logger.error(f"DATABASE INTEGRITY ERROR: {error_details}")
            raise ValueError("Update failed due to database integrity error")

    @staticmethod
    def delete(db: Session, product_id: int) -> None:
        product = db.get(Product, product_id)
        if not product:
            raise ValueError("Product not found")

        try:
            # Si tienes cascade="all, delete-orphan" en tu modelo,
            # SQLAlchemy marcará las imágenes para borrado automáticamente aquí.

            # 1. Aquí llamarías a un servicio para borrar de la nube
            # for img in product.images:
            #     CloudinaryService.delete_image(img.public_id)
            db.delete(product)
            db.commit()
        except IntegrityError as e:
            db.rollback()
            logger.error(f"DATABASE INTEGRITY ERROR (DELETE): {str(e.orig)}")
            raise ValueError(
                "The product cannot be deleted because it is referenced by other records."
            )
