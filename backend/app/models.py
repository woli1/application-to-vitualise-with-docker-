from datetime import date, datetime
from enum import Enum

from sqlalchemy import Date, DateTime, Enum as SqlEnum, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class UserRole(str, Enum):
    student = "student"
    teacher = "teacher"
    supervisor = "supervisor"


class RequestStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(80))
    last_name: Mapped[str] = mapped_column(String(80))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(SqlEnum(UserRole, native_enum=False, length=20), default=UserRole.student)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    taught_courses: Mapped[list["Course"]] = relationship(back_populates="teacher")
    grades: Mapped[list["Grade"]] = relationship(back_populates="student")


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)
    teacher_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))

    teacher: Mapped[User | None] = relationship(back_populates="taught_courses")
    grades: Mapped[list["Grade"]] = relationship(back_populates="course", cascade="all, delete-orphan")


class Grade(Base):
    __tablename__ = "grades"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"))
    value: Mapped[float] = mapped_column(Numeric(4, 2))
    graded_on: Mapped[date] = mapped_column(Date, default=date.today)

    student: Mapped[User] = relationship(back_populates="grades")
    course: Mapped[Course] = relationship(back_populates="grades")


class RegistrationRequest(Base):
    __tablename__ = "registration_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(80))
    last_name: Mapped[str] = mapped_column(String(80))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    requested_role: Mapped[UserRole] = mapped_column(SqlEnum(UserRole, native_enum=False, length=20), default=UserRole.student)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[RequestStatus] = mapped_column(SqlEnum(RequestStatus, native_enum=False, length=20), default=RequestStatus.pending)
    requested_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
