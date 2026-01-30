from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.database.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate


class ProductService:

    @staticmethod
    def create(db: Session, product_data: ProductCreate) -> Product:
        product = Product(**product_data.model_dump())
        db.add(product)
        try:
            db.commit()
            db.refresh(product)
            return product
        except IntegrityError:
            db.rollback()
            raise ValueError("The product cannot be created!")

    @staticmethod
    def get_all(db: Session) -> list[Product]:
        # * scalars convierte el result en objeto itereable | scalar es para solo devolver on campo
        return db.scalars(select(Product)).all()

    @staticmethod
    def get(db: Session, product_id: int) -> Product | None:
        return db.get(Product, product_id)

    @staticmethod
    def update(db: Session, product_id: int, product: ProductUpdate) -> Product | None:
        product = db.get(Product, product_id)
        if not product:
            raise ValueError("Product not found")
        update_fields = product.model_dump(exclude_unset=True)
        for field, value in update_fields.items():
            setattr(product, field, value)
        db.commit()
        db.refresh(product)
        return product

    @staticmethod
    def delete(db: Session, product_id: int) -> None:
        product = db.get(Product, product_id)
        if not product:
            raise ValueError("Product not found")
        db.delete(product)
        db.commit()
