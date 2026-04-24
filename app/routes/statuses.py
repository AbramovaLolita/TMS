from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from app.db.database import db_dependency
from app.db.models import Status, TestResult, User
from app.schemas.statuses import StatusResponse, StatusCreate
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/api/statuses", tags=["statuses"])


@router.post("/", response_model=StatusResponse)
def create_status(
        status: StatusCreate,
        db: db_dependency,
        current_user: User = Depends(get_current_user)
):
    """создание статуса"""

    # Проверка существования статуса
    existing_status = db.query(Status).filter(
        Status.name == status.name
    ).first()

    if existing_status:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Status '{status.name}' already exists"
        )

    db_status = Status(name=status.name)
    db.add(db_status)
    db.commit()
    db.refresh(db_status)
    return db_status


@router.get("/", response_model=List[StatusResponse])
def get_statuses(
        db: db_dependency,
        current_user: User = Depends(get_current_user)  # для единообразия
):
    """ получение списка всех статусов"""
    return db.query(Status).all()


@router.delete("/{status_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_status(
        status_id: int,
        db: db_dependency,
        current_user: User = Depends(get_current_user)
):
    """удаление статуса"""

    db_status = db.query(Status).filter(Status.id == status_id).first()

    if not db_status:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Status not found")

    # проверяем, не используется ли этот статус в testresults
    is_used = db.query(TestResult).filter(
        TestResult.status_id == status_id
    ).first()

    if is_used:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Cannot delete status that is used in test results")

    # проверяем, не удаляем ли базовые статусы
    if status_id in [1, 2, 3, 4]:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Cannot delete default status (passed, failed, skipped, pending)")

    db.delete(db_status)
    db.commit()

    return None