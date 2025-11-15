from sqlalchemy import create_engine, func, desc, select, and_
from sqlalchemy.orm import sessionmaker
from models import Group, Student, Teacher, Subject, Grade

DATABASE_URL = "postgresql://postgres:mysecretpassword@127.0.0.1:5433/postgres"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)


def get_sample_ids(session):
    group_id = session.query(Group.id).first()[0]
    subject_id = session.query(Subject.id).first()[0]
    teacher_id = session.query(Teacher.id).first()[0]
    student_id = session.query(Student.id).first()[0]
    return group_id, subject_id, teacher_id, student_id


def select_1():
    """Знайти 5 студентів із найбільшим середнім балом з усіх предметів."""
    with Session() as session:
        result = (
            session.query(
                Student.fullname,
                func.round(func.avg(Grade.grade), 2).label("avg_grade"),
            )
            .select_from(Student)
            .join(Grade)
            .group_by(Student.id)
            .order_by(desc("avg_grade"))
            .limit(5)
            .all()
        )
        print("\n--- 1. Топ 5 студентів за середнім балом ---")
        for fullname, avg_grade in result:
            print(f"Студент: {fullname}, Середній бал: {avg_grade}")
        return result


def select_2(subject_id):
    """Знайти студента із найвищим середнім балом з певного предмета."""
    with Session() as session:
        subject_name = (
            session.query(Subject.name).filter(Subject.id == subject_id).scalar()
        )

        result = (
            session.query(
                Student.fullname,
                func.round(func.avg(Grade.grade), 2).label("avg_grade"),
            )
            .select_from(Grade)
            .join(Student)
            .filter(Grade.subject_id == subject_id)
            .group_by(Student.id)
            .order_by(desc("avg_grade"))
            .limit(1)
            .first()
        )
        print(f"\n--- 2. Найкращий студент з предмета '{subject_name}' ---")
        if result:
            print(f"Студент: {result[0]}, Середній бал: {result[1]}")
        else:
            print("Дані відсутні.")
        return result


def select_3(subject_id):
    """Знайти середній бал у групах з певного предмета."""
    with Session() as session:
        subject_name = (
            session.query(Subject.name).filter(Subject.id == subject_id).scalar()
        )

        result = (
            session.query(
                Group.name, func.round(func.avg(Grade.grade), 2).label("avg_grade")
            )
            .select_from(Grade)
            .join(Student)
            .join(Group)
            .filter(Grade.subject_id == subject_id)
            .group_by(Group.name)
            .all()
        )
        print(f"\n--- 3. Середній бал у групах з предмета '{subject_name}' ---")
        for group_name, avg_grade in result:
            print(f"Група: {group_name}, Середній бал: {avg_grade}")
        return result


def select_4():
    """Знайти середній бал на потоці (по всій таблиці оцінок)."""
    with Session() as session:
        result = session.query(
            func.round(func.avg(Grade.grade), 2).label("overall_avg")
        ).scalar()
        print("\n--- 4. Середній бал на потоці ---")
        print(f"Загальний середній бал: {result}")
        return result


def select_5(teacher_id):
    """Знайти які курси читає певний викладач."""
    with Session() as session:
        teacher_name = (
            session.query(Teacher.fullname).filter(Teacher.id == teacher_id).scalar()
        )
        result = (
            session.query(Subject.name).filter(Subject.teacher_id == teacher_id).all()
        )
        print(f"\n--- 5. Курси, які читає викладач {teacher_name} ---")
        for (subject_name,) in result:
            print(f"- {subject_name}")
        return result


def select_6(group_id):
    """Знайти список студентів у певній групі."""
    with Session() as session:
        group_name = session.query(Group.name).filter(Group.id == group_id).scalar()
        result = (
            session.query(Student.fullname)
            .filter(Student.group_id == group_id)
            .order_by(Student.fullname)
            .all()
        )
        print(f"\n--- 6. Список студентів у групі '{group_name}' ---")
        for (fullname,) in result:
            print(f"- {fullname}")
        return result


def select_7(group_id, subject_id):
    """Знайти оцінки студентів у окремій групі з певного предмета."""
    with Session() as session:
        group_name = session.query(Group.name).filter(Group.id == group_id).scalar()
        subject_name = (
            session.query(Subject.name).filter(Subject.id == subject_id).scalar()
        )

        result = (
            session.query(Student.fullname, Grade.grade)
            .select_from(Grade)
            .join(Student)
            .join(Group)
            .filter(and_(Student.group_id == group_id, Grade.subject_id == subject_id))
            .order_by(Student.fullname, Grade.grade_date)
            .all()
        )
        print(
            f"\n--- 7. Оцінки студентів групи '{group_name}' з предмета '{subject_name}' ---"
        )
        if result:
            # Групуємо для кращого відображення
            grouped_results = {}
            for fullname, grade in result:
                if fullname not in grouped_results:
                    grouped_results[fullname] = []
                grouped_results[fullname].append(grade)

            for student, grades in grouped_results.items():
                print(f"Студент: {student}, Оцінки: {grades}")
        else:
            print("Оцінки відсутні.")
        return result


def select_8(teacher_id):
    """Знайти середній бал, який ставить певний викладач зі своїх предметів."""
    with Session() as session:
        teacher_name = (
            session.query(Teacher.fullname).filter(Teacher.id == teacher_id).scalar()
        )

        result = (
            session.query(
                Subject.name, func.round(func.avg(Grade.grade), 2).label("avg_grade")
            )
            .select_from(Subject)
            .join(Teacher)
            .join(Grade)
            .filter(Teacher.id == teacher_id)
            .group_by(Subject.name)
            .all()
        )

        overall_avg = (
            session.query(func.round(func.avg(Grade.grade), 2))
            .select_from(Grade)
            .join(Subject)
            .filter(Subject.teacher_id == teacher_id)
            .scalar()
        )

        print(f"\n--- 8. Середній бал, який ставить викладач {teacher_name} ---")
        for subject_name, avg_grade in result:
            print(f"- Предмет '{subject_name}': Середній бал {avg_grade}")
        print(f"Загальний середній бал від викладача: {overall_avg}")
        return result


def select_9(student_id):
    """Знайти список курсів, які відвідує певний студент (з яких має оцінки)."""
    with Session() as session:
        student_name = (
            session.query(Student.fullname).filter(Student.id == student_id).scalar()
        )
        result = (
            session.query(Subject.name)
            .select_from(Subject)
            .join(Grade)
            .join(Student)
            .filter(Student.id == student_id)
            .distinct()
            .all()
        )
        print(f"\n--- 9. Курси, які відвідує студент {student_name} ---")
        for (subject_name,) in result:
            print(f"- {subject_name}")
        return result


def select_10(student_id, teacher_id):
    """Список курсів, які певному студенту читає певний викладач."""
    with Session() as session:
        student_name = (
            session.query(Student.fullname).filter(Student.id == student_id).scalar()
        )
        teacher_name = (
            session.query(Teacher.fullname).filter(Teacher.id == teacher_id).scalar()
        )

        result = (
            session.query(Subject.name)
            .select_from(Subject)
            .join(Grade)
            .join(Student)
            .join(Teacher)
            .filter(and_(Student.id == student_id, Teacher.id == teacher_id))
            .distinct()
            .all()
        )
        print(
            f"\n--- 10. Курси, які студент {student_name} відвідує у викладача {teacher_name} ---"
        )
        for (subject_name,) in result:
            print(f"- {subject_name}")
        return result


if __name__ == "__main__":
    with Session() as session:
        try:
            group_id, subject_id, teacher_id, student_id = get_sample_ids(session)
        except:
            print("Помилка: База даних порожня. Запустіть seed.py спочатку.")
            exit()

    select_1()
    select_2(subject_id)
    select_3(subject_id)
    select_4()
    select_5(teacher_id)
    select_6(group_id)
    select_7(group_id, subject_id)
    select_8(teacher_id)
    select_9(student_id)
    select_10(student_id, teacher_id)
