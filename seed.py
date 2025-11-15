import random
from datetime import datetime, timedelta
from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Group, Student, Teacher, Subject, Grade, Base

DATABASE_URL = "postgresql://postgres:mysecretpassword@127.0.0.1:5433/postgres"

engine = create_engine(DATABASE_URL)
Base.metadata.bind = engine
Session = sessionmaker(bind=engine)
session = Session()

fake = Faker("uk_UA")


def seed_data():
    try:
        groups = [Group(name=f"Group-{i+1}") for i in range(3)]
        session.add_all(groups)
        session.commit()
        print("Groups created.")

        teachers = [Teacher(fullname=fake.name()) for _ in range(5)]
        session.add_all(teachers)
        session.commit()
        print("Teachers created.")

        teacher_ids = [t.id for t in teachers]

        subjects_data = [
            ("Математичний аналіз", teacher_ids[0]),
            ("Основи програмування", teacher_ids[1]),
            ("Бази даних (SQL)", teacher_ids[1]),
            ("Алгоритми і структури даних", teacher_ids[2]),
            ("Комп'ютерні мережі", teacher_ids[3]),
            ("Системний аналіз", teacher_ids[4]),
            ("Фізика", teacher_ids[0]),
            ("Англійська мова", teacher_ids[3]),
        ]
        subjects = [Subject(name=name, teacher_id=tid) for name, tid in subjects_data]
        session.add_all(subjects)
        session.commit()
        print("Subjects created.")

        subject_ids = [s.id for s in subjects]

        students = []
        for i in range(50):
            group_id = random.choice([g.id for g in groups])
            students.append(Student(fullname=fake.name(), group_id=group_id))
        session.add_all(students)
        session.commit()
        print("Students created.")

        student_ids = [s.id for s in students]

        grades = []
        start_date = datetime(2024, 9, 1)
        end_date = datetime(2025, 1, 15)

        for student_id in student_ids:
            student_subjects = random.sample(
                subject_ids, k=random.randint(4, len(subject_ids))
            )

            for subject_id in student_subjects:
                num_grades = random.randint(5, 20)
                for _ in range(num_grades):

                    random_date = start_date + timedelta(
                        days=random.randint(0, (end_date - start_date).days)
                    )

                    grade_value = random.randint(60, 100)

                    grades.append(
                        Grade(
                            student_id=student_id,
                            subject_id=subject_id,
                            grade=grade_value,
                            grade_date=random_date.date(),
                        )
                    )

        session.add_all(grades)
        session.commit()
        print(f"Grades created. Total: {len(grades)}")

    except Exception as e:
        session.rollback()
        print(f"An error occurred: {e}")
    finally:
        session.close()
        print("Seeding finished.")


if __name__ == "__main__":
    seed_data()
