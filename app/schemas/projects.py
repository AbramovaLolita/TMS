from pydantic import BaseModel


# создание проекта
class ProjectCreate(BaseModel):
    title: str

# ответ пользователю
class ProjectResponse(BaseModel):
    id: int
    title: str
    owner_id: int

    class Config:
        from_attributes = True

# обновление проекта
class ProjectUpdate(BaseModel):
    title: str
    owner_id: int