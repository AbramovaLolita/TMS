from fastapi import APIRouter, HTTPException, status, Depends

from typing import List

from app.schemas.testcases import TestCaseCreate, TestCaseResponse, TestCaseUpdate
from app.db.database import db_dependency
from app.db.models import TestCase, Project, User
from app.core.dependencies import get_current_user

project_router = APIRouter(prefix="/api/projects/{project_id}/testcases", tags=["testcases"])

@project_router.post("/", response_model=TestCaseResponse, status_code=status.HTTP_201_CREATED)
def create_testcase_in_project(
        project_id: int,
        testcase: TestCaseCreate,
        db: db_dependency,
        current_user: User = Depends(get_current_user)
):
    """Создать тест-кейс в конкретном проекте"""
    # проверяем наличие проекта
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Project not found")

    # создаем тест-кейс, привязанный к этому проекту
    db_testcase = TestCase(
        title=testcase.title,
        description=testcase.description,
        steps=testcase.steps,
        expected_result=testcase.expected_result,
        project_id=project_id
    )
    db.add(db_testcase)
    db.commit()
    db.refresh(db_testcase)
    return db_testcase


@project_router.get("/", response_model=List[TestCaseResponse])
def get_project_testcases(
        project_id: int,
        db: db_dependency,
        current_user: User = Depends(get_current_user)  # добавить
):
    """
    Получение списка всех тест-кейсов.
    """
    project = db.query(Project).filter(Project.id == project_id,
                                       Project.owner_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Project not found")

    return project.testcases

router = APIRouter(prefix="/api/testcases", tags=["testcases"])


@router.get("/{testcase_id}", response_model=TestCaseResponse)
def get_testcase(
        testcase_id: int,
        db: db_dependency,
        current_user: User = Depends(get_current_user)
):
    testcase = db.query(TestCase).join(Project).filter(
        TestCase.id == testcase_id,
        Project.owner_id == current_user.id
    ).first()

    if not testcase:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail= "Testcase not found")

    return testcase


@router.put("/{testcase_id}", response_model=TestCaseResponse)
def update_testcase(
        testcase_id: int,
        testcase: TestCaseUpdate,
        db: db_dependency,
        current_user: User = Depends(get_current_user)
):
    db_testcase = db.query(TestCase).join(Project).filter(
        TestCase.id == testcase_id,
        Project.owner_id == current_user.id
    ).first()

    if not db_testcase:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail= f"Testcase not found")
    # обновляем поля
    for key, value in testcase.model_dump(exclude_unset=True).items():
        setattr(db_testcase, key, value)

    # сохраняем изменения
    db.commit()
    db.refresh(db_testcase)

    return db_testcase


@router.delete("/{testcase_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_testcase(
        testcase_id: int,
        db: db_dependency,
        current_user: User = Depends(get_current_user)
):
    """
    Удаление тест-кейса.
    """
    # проверка наличия тест-кейса
    db_testcase = db.query(TestCase).join(Project).filter(
        TestCase.id == testcase_id,
        Project.owner_id == current_user.id
    ).first()

    if not db_testcase:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail= f"Testcase not found")

    # удаление тест-кейса
    db.delete(db_testcase)
    # сохранение
    db.commit()

    return None


