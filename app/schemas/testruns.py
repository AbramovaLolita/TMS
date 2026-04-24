from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class TestRunCreate(BaseModel):
    title: str
    description: Optional[str] = None
    testcase_ids: List[int] = []


class TestRunResponse(BaseModel):
    id: int
    title: str
    project_id: int
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: str  # pending, running, completed, cancelled
    description: Optional[str] = None
    owner_id: int


    class Config:
        from_attributes = True


class TestRunUpdate(BaseModel):
    title: str
    description: Optional[str] = None
    status: str  # pending, running, completed, cancelled
    project_id: int


class TestRunStart(BaseModel):
    """Для запуска прогона"""
    pass  # можно добавить комментарий


class TestRunComplete(BaseModel):
    """Для завершения прогона"""
    pass