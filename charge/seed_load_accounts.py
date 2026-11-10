import sys
from pathlib import Path

project_root = Path("/app")
if not (project_root / "métier").exists():
    project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from datetime import date

from sqlalchemy import select

from métier.app.database import Base, SessionLocal, engine
from métier.app.models import Course, Grade, User, UserRole


def main() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        course = db.scalar(select(Course).where(Course.name == "Charge - parcours étudiant"))
        if not course:
            course = Course(name="Charge - parcours étudiant")
            db.add(course)
            db.flush()
        for index in range(1, 21):
            email = f"charge{index:02d}@etu.univ-amu.fr"
            user = db.scalar(select(User).where(User.email == email))
            if not user:
                user = User(
                    first_name=f"Charge{index:02d}",
                    last_name="Test",
                    email=email,
                    password_hash="demo",
                    role=UserRole.student,
                )
                db.add(user)
                db.flush()
            if not db.scalar(select(Grade).where(Grade.student_id == user.id, Grade.course_id == course.id)):
                db.add(Grade(student_id=user.id, course_id=course.id, value=15, graded_on=date.today()))
        db.commit()
    print("20 comptes de charge disponibles.")


if __name__ == "__main__":
    main()
