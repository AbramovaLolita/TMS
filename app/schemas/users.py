from pydantic import BaseModel, field_validator

# регистрация пользователя
class UserCreate(BaseModel):
    username: str
    password: str
    #confirm_password: str
    email: str

    # валидация на уровне схемы
    # @field_validator('confirm_password')
    # @classmethod
    # def passwords_match(cls, v: str, info) -> str:
    #     if 'password' in info.data and v != info.data['password']:
    #         raise ValueError('Passwords do not match')
    #     return v

# ответ пользователю
class UserResponse(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True

# обновление логина или пароля
class UserUpdate(BaseModel):
    password: str
    email: str
