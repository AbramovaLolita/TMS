from datetime import datetime
from typing import Annotated

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column, Session

from fastapi import Depends
from app.config import get_db_url

DATABASE_URL = get_db_url()

# запуск
engine = create_engine(DATABASE_URL)

# фабрика сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# генератор сессий
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
int_pk = Annotated[int, mapped_column(primary_key=True)]
created_at = Annotated[datetime, mapped_column(server_default=func.now())]
updated_at = Annotated[datetime, mapped_column(server_default=func.now(), onupdate=func.now())]
str_uniq = Annotated[str, mapped_column(unique=True, nullable=False)]
str_null_true = Annotated[str, mapped_column(nullable=True)]
str_null_false = Annotated[str, mapped_column(nullable=False)]

# базовый класс
class Base(DeclarativeBase):
    __abstract__ = True
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
