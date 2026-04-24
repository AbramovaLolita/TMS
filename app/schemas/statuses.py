from pydantic import BaseModel

class StatusCreate(BaseModel):
    name: str

class StatusResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class StatusUpdate(BaseModel):
    name: str
