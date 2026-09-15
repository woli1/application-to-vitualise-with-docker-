from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select, text
from sqlalchemy.orm import Session, joinedload

from .database import Base, engine, get_db
from .models import Course, Grade, RegistrationRequest, RequestStatus, User, UserRole
from .schemas import CourseResponse, GradeCreate, GradeResponse, GradeUpdate, LoginRequest, LoginResponse, RegistrationCreate, RegistrationResponse, UserSummary

Base.metadata.create_all(bind=engine)
with engine.begin() as connection:
    connection.execute(text("ALTER TABLE registration_requests ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255)"))
app = FastAPI(title="Notes API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/auth/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == payload.email))
    if not user or not user.is_active or user.password_hash != payload.password:
        raise HTTPException(status_code=401, detail="Identifiant ou mot de passe incorrect")
    return user


@app.get("/api/students", response_model=list[UserSummary])
def students(db: Session = Depends(get_db)):
    return db.scalars(select(User).where(User.role == UserRole.student).order_by(User.last_name, User.first_name)).all()


@app.get("/api/students/{student_id}/grades", response_model=list[GradeResponse])
def student_grades(student_id: int, db: Session = Depends(get_db)):
    grades = db.scalars(
        select(Grade).options(joinedload(Grade.course)).where(Grade.student_id == student_id).order_by(Grade.graded_on)
    ).all()
    return [GradeResponse(id=g.id, course=g.course.name, value=float(g.value), graded_on=g.graded_on) for g in grades]


@app.get("/api/courses", response_model=list[CourseResponse])
def courses(db: Session = Depends(get_db)):
    records = db.scalars(select(Course).options(joinedload(Course.teacher)).order_by(Course.name)).all()
    return [CourseResponse(id=c.id, name=c.name, teacher=f"{c.teacher.first_name} {c.teacher.last_name}" if c.teacher else None) for c in records]


@app.get("/api/courses/{course_id}/grades", response_model=list[GradeResponse])
def course_grades(course_id: int, db: Session = Depends(get_db)):
    grades = db.scalars(select(Grade).options(joinedload(Grade.student), joinedload(Grade.course)).where(Grade.course_id == course_id)).all()
    return [GradeResponse(id=g.id, course=f"{g.student.first_name} {g.student.last_name}", value=float(g.value), graded_on=g.graded_on) for g in grades]


@app.post("/api/courses/{course_id}/grades", response_model=GradeResponse, status_code=201)
def add_grade(course_id: int, payload: GradeCreate, db: Session = Depends(get_db)):
    course = db.get(Course, course_id)
    student = db.get(User, payload.student_id)
    if not course or not student or student.role != UserRole.student:
        raise HTTPException(status_code=404, detail="Cours ou étudiant introuvable")
    existing = db.scalar(select(Grade).where(Grade.course_id == course_id, Grade.student_id == payload.student_id))
    if existing:
        raise HTTPException(status_code=409, detail="Cet étudiant a déjà une note dans ce cours")
    grade = Grade(course_id=course_id, student_id=student.id, value=payload.value, graded_on=payload.graded_on)
    db.add(grade)
    db.commit()
    db.refresh(grade)
    return GradeResponse(id=grade.id, course=course.name, value=float(grade.value), graded_on=grade.graded_on)


@app.patch("/api/grades/{grade_id}", response_model=GradeResponse)
def update_grade(grade_id: int, payload: GradeUpdate, db: Session = Depends(get_db)):
    grade = db.scalar(select(Grade).options(joinedload(Grade.student), joinedload(Grade.course)).where(Grade.id == grade_id))
    if not grade:
        raise HTTPException(status_code=404, detail="Note introuvable")
    grade.value = payload.value
    if payload.graded_on:
        grade.graded_on = payload.graded_on
    db.commit()
    db.refresh(grade)
    return GradeResponse(id=grade.id, course=f"{grade.student.first_name} {grade.student.last_name}", value=float(grade.value), graded_on=grade.graded_on)


@app.get("/api/registration-requests", response_model=list[RegistrationResponse])
def registration_requests(db: Session = Depends(get_db)):
    return db.scalars(select(RegistrationRequest).order_by(RegistrationRequest.requested_at)).all()


@app.post("/api/registration-requests", response_model=RegistrationResponse, status_code=201)
def create_registration(payload: RegistrationCreate, db: Session = Depends(get_db)):
    if db.scalar(select(User).where(User.email == payload.email)):
        raise HTTPException(status_code=409, detail="Cette adresse email est déjà utilisée")
    existing = db.scalar(select(RegistrationRequest).where(RegistrationRequest.email == payload.email))
    if existing:
        raise HTTPException(status_code=409, detail="Une demande existe déjà pour cet email")
    request = RegistrationRequest(
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=payload.email,
        requested_role=payload.requested_role,
        password_hash=payload.password,
    )
    db.add(request)
    db.commit()
    db.refresh(request)
    return request


@app.patch("/api/registration-requests/{request_id}/{decision}", response_model=RegistrationResponse)
def decide_registration(request_id: int, decision: str, db: Session = Depends(get_db)):
    request = db.get(RegistrationRequest, request_id)
    if not request or decision not in {"approve", "reject"}:
        raise HTTPException(status_code=404, detail="Demande ou décision invalide")
    if decision == "approve":
        if not request.password_hash:
            raise HTTPException(status_code=409, detail="Cette ancienne demande doit être recréée")
        if db.scalar(select(User).where(User.email == request.email)):
            raise HTTPException(status_code=409, detail="Ce compte existe déjà")
        db.add(User(
            first_name=request.first_name,
            last_name=request.last_name,
            email=request.email,
            password_hash=request.password_hash,
            role=request.requested_role,
        ))
    request.status = RequestStatus.approved if decision == "approve" else RequestStatus.rejected
    db.commit()
    db.refresh(request)
    return request


client_dir = Path(__file__).resolve().parents[2] / "client"
app.mount("/", StaticFiles(directory=client_dir, html=True), name="client")
