from fastapi import APIRouter, HTTPException, status, Depends

from typing import List

from app.schemas.testresults import TestResultResponse,TestResultUpdate
from app.db.database import db_dependency
from app.db.models import TestResult, User, Project, TestRun, Status
from app.core.dependencies import get_current_user

project_router = APIRouter(prefix="/api/projects/{project_id}/testresults", tags=["testresults"])

@project_router.get("/", response_model=List[TestResultResponse])
def get_project_testresults(
        project_id: int,
        db: db_dependency,
        current_user: User = Depends(get_current_user)  # добавить
):
    """
    Получение списка результатов прогонов
    """
    project = db.query(Project).filter(Project.id == project_id,
                                       Project.owner_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Project not found")
    # получаем все результаты тестирования для проекта
    testresults = db.query(TestResult).join(TestRun).join(Project).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id
    ).all()

    return testresults


router = APIRouter(prefix="/api/testresults", tags=["testresults"])

@router.get("/{testresult_id}", response_model=TestResultResponse)
def get_testresult(
        testresult_id: int,
        db: db_dependency,
        current_user: User = Depends(get_current_user)
):
    testresult = db.query(TestResult).join(TestRun).join(Project).filter(
        TestResult.id == testresult_id,
        Project.owner_id == current_user.id
    ).first()

    if not testresult:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail= "Result not found")

    return testresult


@router.get("/testrun/{testrun_id}", response_model=List[TestResultResponse])
def get_testrun_results(
        testrun_id: int,
        db: db_dependency,
        current_user: User = Depends(get_current_user)
):
    """Получить все результаты конкретного прогона"""

    # Проверяем, что прогон принадлежит пользователю
    testrun = db.query(TestRun).join(Project).filter(
        TestRun.id == testrun_id,
        Project.owner_id == current_user.id
    ).first()

    if not testrun:
        raise HTTPException(404, "Test run not found")

    # Получаем результаты с подгрузкой тест-кейсов
    results = db.query(TestResult).filter(
        TestResult.testrun_id == testrun_id
    ).all()

    return results

@router.put("/{testresult_id}", response_model=TestResultResponse)
def update_testresult(
        testresult_id: int,
        result: TestResultUpdate,  # нужно создать схему
        db: db_dependency,
        current_user: User = Depends(get_current_user)
):
    testresult = db.query(TestResult).join(TestRun).join(Project).filter(
        TestResult.id == testresult_id,
        Project.owner_id == current_user.id
    ).first()
    if hasattr(result, 'testcase_id') and result.testcase_id is not None:
        raise HTTPException(400, "Changing testcase_id is not allowed")
    if not testresult:
        raise HTTPException(404, "Result not found")

    if result.status_id is not None:
        testresult.status_id = result.status_id
    if result.comm is not None:
        testresult.comm = result.comm

    db.commit()
    db.refresh(testresult)
    return testresult


# app/routes/testresults.py
@router.get("/testrun/{testrun_id}/stats")
def get_testrun_stats(
        testrun_id: int,
        db: db_dependency,
        current_user: User = Depends(get_current_user)
):
    """Получить статистику по прогону"""

    # Проверяем права доступа
    testrun = db.query(TestRun).join(Project).filter(
        TestRun.id == testrun_id,
        Project.owner_id == current_user.id
    ).first()

    if not testrun:
        raise HTTPException(404, "Test run not found")

    # Получаем все статусы
    statuses = db.query(Status).all()
    status_map = {s.id: s.name for s in statuses}

    # Подсчёт результатов по статусам
    results = db.query(TestResult).filter(
        TestResult.testrun_id == testrun_id
    ).all()

    total = len(results)
    passed = sum(1 for r in results if status_map.get(r.status_id) == 'passed')
    failed = sum(1 for r in results if status_map.get(r.status_id) == 'failed')
    skipped = sum(1 for r in results if status_map.get(r.status_id) == 'skipped')
    pending = sum(1 for r in results if status_map.get(r.status_id) == 'pending')

    success_rate = round((passed / total) * 100) if total > 0 else 0

    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "pending": pending,
        "success_rate": success_rate
    }