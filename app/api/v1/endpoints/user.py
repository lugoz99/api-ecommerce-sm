from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies.database import get_db
from app.schemas.user import UserCreate, UserRead
from app.services.user_service import UserService

router = APIRouter()


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    return UserService.create_user(db, user)


@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: int, db: Session = Depends(get_db)):
    return UserService.get_user(db, user_id)
