from fastapi import APIRouter, HTTPException, status, Depends

from typing import List

from app.schemas.projects import ProjectCreate, ProjectResponse, ProjectUpdate
from app.db.database import db_dependency
from app.db.models import Project, User, TestCase
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/api/projects", tags=["projects"])

@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(project: ProjectCreate,
                   db: db_dependency,
                   current_user: User = Depends(get_current_user)):
    """
    Создание проекта.
    """
    # проверка уникальности проекта
    existing_project = db.query(Project).filter(
        Project.title == project.title
    ).first()

    if existing_project:
        raise HTTPException(409, "Project already exists")

    # создаем проект
    db_project = Project(title=project.title,
                         owner_id=current_user.id)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)

    return db_project


@router.get("/", response_model=List[ProjectResponse])
def get_projects(
        db: db_dependency,
        skip: int = 0,
        limit: int = 100,
        current_user: User = Depends(get_current_user)  # добавить
):
    """
    Получение списка всех проектов.
    """
    projects = db.query(Project).filter(Project.owner_id==current_user.id).offset(skip).limit(limit).all()
    return projects


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
        project_id: int,  # id проекта из URL
        db: db_dependency,
        current_user: User = Depends(get_current_user)
):
    """
    Получение конкретного проекта по его ID.
    """
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(404, f"Project with id {project_id} not found" )
    return project


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
        project_id: int,
        project: ProjectUpdate,
        db: db_dependency,
        current_user: User = Depends(get_current_user)  # добавить
):
    """
    Обновление существующего проекта.
    """
    db_project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id
    ).first()

    # проверка наличия проекта
    if not db_project:
        raise HTTPException(404, f"Project with id {project_id} not found")

    # обновление полей
    update_data = project.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_project, key, value)

    # сохранение изменений
    db.commit()
    db.refresh(db_project)

    return db_project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
        project_id: int,
        db: db_dependency,
        current_user: User = Depends(get_current_user)
):
    """
    каскадное удаление проекта с тест-кейсами
    """
    # поиск проекта
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id
    ).first()

    #  существование проекта
    if not project:
        raise HTTPException(404, f"Project with id {project_id} not found" )
    
    # удаляем тест-кейсы
    db.query(TestCase).filter(TestCase.project_id == project_id).delete()

    # удаляем проект
    db.delete(project)

    # сохранение
    db.commit()

    return None


