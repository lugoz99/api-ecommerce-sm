from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.orm import Session
from app.api.dependencies.database import get_db
from app.schemas.category import CategoryCreate, CategoryResponse
from app.services.category_service import CategoryService

router = APIRouter()


@router.post("/", response_model=CategoryResponse)
def post_category(category: CategoryCreate, db: Session = Depends(get_db)):
    service = CategoryService()
    return service.create(db, category)


@router.post("/bulk", response_model=list[CategoryResponse])
def post_categories(categories: list[CategoryCreate], db: Session = Depends(get_db)):
    service = CategoryService()
    return service.bulk_create(db, categories)


@router.get("/", response_model=list[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    service = CategoryService()
    return service.get(db)


@router.put("/{id}")
def update_category(id: int, category: CategoryCreate, db: Session = Depends(get_db)):
    service = CategoryService()
    return service.update(db, id, category)


@router.delete("/{id}")
def delete_category(id: int, db: Session = Depends(get_db)):
    service = CategoryService()
    return service.delete(db, id)
