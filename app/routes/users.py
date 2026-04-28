from fastapi import APIRouter, HTTPException, status, Depends
from passlib.context import CryptContext
from typing import List
from app.schemas.users import UserCreate, UserResponse, UserUpdate
from app.db.database import db_dependency
from app.db.models import  User
from app.core.dependencies import get_current_user



# настройка хэширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def hash_password(password: str) -> str:
    return pwd_context.hash(password)
router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: db_dependency):
    """
    создание пользователя
    """
    existing_user = db.query(User).filter(
        User.username == user.username
    ).first()
    if existing_user:
        raise HTTPException(409, "User already exists")

    if user.email:
        existing_email = db.query(User).filter(
            User.email == user.email
        ).first()

        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User with email '{user.email}' already exists"
            )

        # создание пользователя
    db_user = User(
        username=user.username,
        password=user.password,
        email=user.email
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user

@router.put('/{user_id}',response_model=UserResponse)
def update_user(
        user_id: int,
        user: UserCreate,
        db: db_dependency
):
    db_user = db.query(User).filter(User.id==user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{user_id} not found"
        )

    if user.password:
        db_user.password = user.password  # потом добавите хэширование

    if user.email:
        db_user.email = user.email

    # сохранение изменений
    db.commit()
    db.refresh(db_user)

    return db_user




user_router = APIRouter(prefix="/api/users", tags=["users"])

@user_router.get("/", response_model=List[UserResponse])
def get_users(
        db: db_dependency,
        current_user: User = Depends(get_current_user)  # для единообразия
):
    """ получение списка всех статусов"""
    return db.query(User).all()


@user_router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
        user_id: int,
        db: db_dependency
):
    """
    Удаление проекта.
    Возвращает статус 204 No Content при успешном удалении.
    """

    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{user_id} not found"
        )

    # удаление проекта
    db.delete(db_user)
    # сохранение
    db.commit()
    return None
