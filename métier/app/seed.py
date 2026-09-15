from datetime import date

from sqlalchemy import select

from .database import Base, SessionLocal, engine
from .models import Course, Grade, RegistrationRequest, RequestStatus, User, UserRole


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.scalar(select(User).where(User.email == "abdelhamid.tan@etu.univ-amu.fr")):
            if not db.scalar(select(User).where(User.email == "superviseur@ecole.fr")):
                db.add(User(first_name="S.", last_name="Superviseur", email="superviseur@ecole.fr", password_hash="demo", role=UserRole.supervisor))
                db.commit()
            return
        student = User(first_name="Abdelhamid", last_name="Tan", email="abdelhamid.tan@etu.univ-amu.fr", password_hash="demo", role=UserRole.student)
        teacher = User(first_name="M.", last_name="Ksouri", email="m.ksouri@ecole.fr", password_hash="demo", role=UserRole.teacher)
        supervisor = User(first_name="S.", last_name="Superviseur", email="superviseur@ecole.fr", password_hash="demo", role=UserRole.supervisor)
        db.add_all([student, teacher, supervisor])
        db.flush()
        courses = [Course(name="Informatique 101", teacher_id=teacher.id), Course(name="Mathématiques", teacher_id=teacher.id), Course(name="Anglais B2", teacher_id=teacher.id), Course(name="Physique", teacher_id=teacher.id)]
        db.add_all(courses)
        db.flush()
        db.add_all([
            Grade(student_id=student.id, course_id=courses[0].id, value=18, graded_on=date(2026, 9, 12)),
            Grade(student_id=student.id, course_id=courses[1].id, value=14, graded_on=date(2026, 9, 15)),
            Grade(student_id=student.id, course_id=courses[2].id, value=16, graded_on=date(2026, 9, 18)),
            Grade(student_id=student.id, course_id=courses[3].id, value=11, graded_on=date(2026, 9, 20)),
        ])
        db.add_all([
            RegistrationRequest(first_name="Jean", last_name="Dupont", email="jean.dupont@ecole.fr", requested_role=UserRole.student, status=RequestStatus.pending),
            RegistrationRequest(first_name="Marie", last_name="Martin", email="marie.martin@ecole.fr", requested_role=UserRole.teacher, status=RequestStatus.pending),
            RegistrationRequest(first_name="Lucas", last_name="Bernard", email="lucas.bernard@ecole.fr", requested_role=UserRole.student, status=RequestStatus.pending),
        ])
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    seed()
