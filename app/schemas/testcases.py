from pydantic import BaseModel
from typing import Optional


class TestCaseCreate(BaseModel):
    title: str
    description: Optional[str] = None
    steps: Optional[str] = None
    expected_result: Optional[str] = None
    #project_id: int


class TestCaseResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    steps: Optional[str] = None
    expected_result: Optional[str] = None
    project_id: int

    class Config:
        from_attributes = True

class TestCaseUpdate(BaseModel):
    title: str
    description: Optional[str] = None
    steps: Optional[str] = None
    expected_result: Optional[str] = None
    project_id: int
