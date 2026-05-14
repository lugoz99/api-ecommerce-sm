from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies.database import get_db
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate
from app.services.category_service import CategoryService

router = APIRouter()


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def post_category(category: CategoryCreate, db: Session = Depends(get_db)):
    return CategoryService.create(db, category)


@router.post(
    "/bulk", response_model=list[CategoryResponse], status_code=status.HTTP_201_CREATED
)
def post_categories(categories: list[CategoryCreate], db: Session = Depends(get_db)):
    return CategoryService.bulk_create(db, categories)


@router.get("/", response_model=list[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    return CategoryService.get(db)


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    return CategoryService.get_by_id(db, category_id)


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(category_update: CategoryUpdate, db: Session = Depends(get_db)):
    return CategoryService.update(db, category_update)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    CategoryService.delete(db, category_id)
