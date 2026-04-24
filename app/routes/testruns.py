from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from app.schemas.testruns import TestRunCreate, TestRunResponse, TestRunUpdate
from app.db.database import db_dependency
from app.db.models import Project, TestRun, TestCase, TestResult, Status, User
from app.core.dependencies import get_current_user

project_router = APIRouter(prefix="/api/projects/{project_id}/testruns", tags=["testruns"])


@project_router.post("/", response_model=TestRunResponse, status_code=status.HTTP_201_CREATED)
def create_testrun_in_project(
        project_id: int,
        testrun: TestRunCreate,
        db: db_dependency,
        current_user: User = Depends(get_current_user)
):
    """Создать прогон тестов в конкретном проекте"""

    # Проверяем наличие проекта и права доступа
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(404, f"Project with id {project_id} not found")

    # Проверяем уникальность названия прогона в проекте
    existing_testrun = db.query(TestRun).filter(
        TestRun.title == testrun.title,
        TestRun.project_id == project_id
    ).first()

    if existing_testrun:
        raise HTTPException(409, f"Test run '{testrun.title}' already exists in this project")

    # Создаем прогон
    db_testrun = TestRun(
        title=testrun.title,
        description=testrun.description,
        project_id=project_id,
        status="pending",
        owner_id=current_user.id
    )

    db.add(db_testrun)
    db.commit()
    db.refresh(db_testrun)

    # Получаем статус "pending"
    pending_status = db.query(Status).filter(Status.name == "pending").first()

    for testcase_id in testrun.testcase_ids:
        # Проверяем, что тест-кейс принадлежит проекту
        testcase = db.query(TestCase).filter(
            TestCase.id == testcase_id,
            TestCase.project_id == project_id
        ).first()

        if testcase:
            result = TestResult(
                testrun_id=db_testrun.id,
                testcase_id=testcase_id,
                status_id=pending_status.id
            )
            db.add(result)

    db.commit()

    return db_testrun


@project_router.get("/", response_model=List[TestRunResponse])
def get_project_testruns(
        project_id: int,
        db: db_dependency,
        current_user: User = Depends(get_current_user)
):
    """Получить список всех прогонов проекта"""

    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(404, "Project not found")

    return project.testruns


router = APIRouter(prefix="/api/testruns", tags=["testruns"])


@router.get("/{testrun_id}", response_model=TestRunResponse)
def get_testrun(
        testrun_id: int,
        db: db_dependency,
        current_user: User = Depends(get_current_user)
):
    """Получить конкретный прогон по его ID"""

    testrun = db.query(TestRun).join(Project).filter(
        TestRun.id == testrun_id,
        Project.owner_id == current_user.id
    ).first()

    if not testrun:
        raise HTTPException(404, "Testrun not found")

    return testrun


@router.put("/{testrun_id}", response_model=TestRunResponse)
def update_testrun(
        testrun_id: int,
        testrun: TestRunUpdate,
        db: db_dependency,
        current_user: User = Depends(get_current_user)
):
    """Обновить существующий прогон"""

    db_testrun = db.query(TestRun).join(Project).filter(
        TestRun.id == testrun_id,
        Project.owner_id == current_user.id
    ).first()

    if not db_testrun:
        raise HTTPException(404, "Testrun not found")

    # Обновляем поля
    for key, value in testrun.model_dump(exclude_unset=True).items():
        setattr(db_testrun, key, value)

    db.commit()
    db.refresh(db_testrun)

    return db_testrun


@router.delete("/{testrun_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_testrun(
        testrun_id: int,
        db: db_dependency,
        current_user: User = Depends(get_current_user)
):
    """Удалить прогон"""

    testrun = db.query(TestRun).join(Project).filter(
        TestRun.id == testrun_id,
        Project.owner_id == current_user.id
    ).first()

    if not testrun:
        raise HTTPException(404, "Testrun not found")

    # Удаляем связанные результаты (или они удалятся каскадно)
    db.query(TestResult).filter(TestResult.testrun_id == testrun_id).delete()

    db.delete(testrun)
    db.commit()

    return None


# app/routes/testruns.py
from datetime import datetime


@router.post("/{testrun_id}/start", response_model=TestRunResponse)
def start_testrun(
        testrun_id: int,
        db: db_dependency,
        current_user: User = Depends(get_current_user)
):
    """Запустить прогон тестов (меняет статус с pending на running)"""

    # Находим прогон с проверкой прав
    testrun = db.query(TestRun).join(Project).filter(
        TestRun.id == testrun_id,
        Project.owner_id == current_user.id
    ).first()

    if not testrun:
        raise HTTPException(404, "Test run not found")

    # Проверяем, что прогон можно запустить
    if testrun.status != "pending":
        raise HTTPException(400, f"Cannot start test run with status '{testrun.status}'. Only pending can be started.")

    # Обновляем статус и время запуска
    testrun.status = "running"
    testrun.started_at = datetime.utcnow()

    db.commit()
    db.refresh(testrun)

    return testrun


@router.post("/{testrun_id}/complete", response_model=TestRunResponse)
def complete_testrun(
        testrun_id: int,
        db: db_dependency,
        current_user: User = Depends(get_current_user)
):
    """Завершить прогон тестов (меняет статус с running на completed)"""

    # Находим прогон с проверкой прав
    testrun = db.query(TestRun).join(Project).filter(
        TestRun.id == testrun_id,
        Project.owner_id == current_user.id
    ).first()

    if not testrun:
        raise HTTPException(404, "Test run not found")

    # Проверяем, что прогон можно завершить
    if testrun.status != "running":
        raise HTTPException(400,
                            f"Cannot complete test run with status '{testrun.status}'. Only running can be completed.")

    # Обновляем статус и время завершения
    testrun.status = "completed"
    testrun.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(testrun)

    return testrun