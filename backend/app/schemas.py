from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from .models import RequestStatus, UserRole


class UserSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str
    last_name: str
    email: EmailStr
    role: UserRole


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)


class LoginResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    role: UserRole


class GradeResponse(BaseModel):
    id: int
    course: str
    value: float
    graded_on: date


class CourseResponse(BaseModel):
    id: int
    name: str
    teacher: str | None = None


class RegistrationResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    requested_role: UserRole
    status: RequestStatus
    requested_at: datetime


class GradeCreate(BaseModel):
    student_id: int
    value: float = Field(ge=0, le=20)
    graded_on: date | None = None


class GradeUpdate(BaseModel):
    value: float = Field(ge=0, le=20)
    graded_on: date | None = None


class RegistrationCreate(BaseModel):
    first_name: str = Field(min_length=1, max_length=80)
    last_name: str = Field(min_length=1, max_length=80)
    email: EmailStr
    password: str = Field(min_length=6)
    requested_role: UserRole = UserRole.student
