from sqlalchemy import ForeignKey, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.db.database import Base, str_uniq, int_pk, str_null_true, str_null_false


# формирование версии alembic: alembic revision --autogenerate -m "message"
# обновление: alembic upgrade head

# таблица проектов
class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int_pk]
    title: Mapped[str_null_false]
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    # Связи
    owner: Mapped["User"] = relationship(back_populates="projects")
    testcases: Mapped[list["TestCase"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    testruns: Mapped[list["TestRun"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
        passive_deletes=True
    )


class TestCase(Base):
    __tablename__ = "testcases"

    id: Mapped[int_pk]
    title: Mapped[str_null_false]
    description: Mapped[str | None] = mapped_column(Text)
    steps: Mapped[str | None] = mapped_column(Text)
    expected_result: Mapped[str | None] = mapped_column(Text)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"))

    # cвязи
    project: Mapped["Project"] = relationship(back_populates="testcases")
    testresults: Mapped[list["TestResult"]] = relationship(
        back_populates="testcase",
        cascade="all, delete-orphan",
        passive_deletes=True
    )


class TestRun(Base):
    __tablename__ = "testruns"

    id: Mapped[int_pk]
    title: Mapped[str_null_false]
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"))


    # Временные метки
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Статус и описание
    status: Mapped[str] = mapped_column(default="pending")
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # cвязи
    project: Mapped["Project"] = relationship(back_populates="testruns")
    owner: Mapped["User"] = relationship(back_populates="testruns")
    test_results: Mapped[list["TestResult"]] = relationship(
        back_populates="test_run",
        cascade="all, delete-orphan",
        passive_deletes=True
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[int_pk]
    username: Mapped[str_uniq]
    password: Mapped[str_null_false]
    email: Mapped[str_null_true]

    # cвязи
    projects: Mapped[list["Project"]] = relationship(
        back_populates="owner",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    testruns: Mapped[list["TestRun"]] = relationship(
        back_populates="owner",
        cascade="all, delete-orphan",
        passive_deletes=True
    )


class Status(Base):
    __tablename__ = "statuses"

    id: Mapped[int_pk]
    name: Mapped[str_null_false]

    # cвязи
    testresults: Mapped[list["TestResult"]] = relationship(back_populates="status")


class TestResult(Base):
    __tablename__ = "testresults"

    id: Mapped[int_pk]
    testrun_id: Mapped[int] = mapped_column(ForeignKey("testruns.id", ondelete="CASCADE"))
    testcase_id: Mapped[int] = mapped_column(ForeignKey("testcases.id", ondelete="CASCADE"))
    status_id: Mapped[int] = mapped_column(ForeignKey("statuses.id", ondelete="CASCADE"))
    comm: Mapped[str | None] = mapped_column(Text)

    # cвязи
    testcase: Mapped["TestCase"] = relationship(back_populates="testresults")
    test_run: Mapped["TestRun"] = relationship(back_populates="test_results")
    status: Mapped["Status"] = relationship(back_populates="testresults")