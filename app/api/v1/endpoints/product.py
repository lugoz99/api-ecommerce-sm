from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies.database import get_db
from app.schemas.product import ProductCreate, ProductResponse
from app.services.product_service import ProductService

router = APIRouter()


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    return ProductService.create(db, product)


@router.get("/", response_model=list[ProductResponse])
def get_products(db: Session = Depends(get_db)):
    return ProductService.get(db)


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    return ProductService.get_by_id(db, product_id)


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int, product: ProductCreate, db: Session = Depends(get_db)
):
    return ProductService.update(db, product_id, product)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    ProductService.delete(db, product_id)
