from pydantic import BaseModel
from typing import Optional
from app.schemas.testcases import TestCaseResponse

class TestResultUpdate(BaseModel):
    status_id: Optional[int] = None
    comm: Optional[str] = None

class TestResultResponse(BaseModel):
    id: int
    testrun_id: int
    testcase_id: int
    status_id: int
    comm: Optional[str] = None
    testcase: TestCaseResponse | None = None  # ← добавить это поле!


    class Config:
        from_attributes = True