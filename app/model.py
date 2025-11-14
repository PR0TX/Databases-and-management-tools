# model.py
# Увесь доступ до БД (SQLAlchemy ORM)

from __future__ import annotations

import psycopg
from contextlib import contextmanager
from typing import Any

from sqlalchemy import (
    create_engine, select, func, text, update, delete, and_, or_, literal_column
)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

# ORM-сутності (класи-таблиці) та Base
from orm_models import Base, Student, Instructor, Course, Enrollment, Exam


class Model:
    def __init__(self, dsn: str):
        # Нормалізація DSN до формату SQLAlchemy з драйвером psycopg3
        def _normalize(url: str) -> str:
            if url.startswith("postgres://"):
                return url.replace("postgres://", "postgresql+psycopg://", 1)
            if url.startswith("postgresql://"):
                return url.replace("postgresql://", "postgresql+psycopg://", 1)
            return url

        self._dsn = _normalize(dsn)
        self._engine = create_engine(self._dsn, pool_pre_ping=True, future=True)
        self._Session = sessionmaker(bind=self._engine, expire_on_commit=False, future=True)


    def ping(self) -> bool:
        try:
            with self._engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception:
            return False

    @contextmanager
    def _session(self):
        """Єдиний контекст-менеджер для роботи з транзакцією ORM Session."""
        s = self._Session()
        try:
            yield s
            s.commit()
        except IntegrityError as e:
            s.rollback()
            raise e.orig
        except Exception:
            s.rollback()
            raise
        finally:
            s.close()

    # ----------------------------------------------------------------------
    # CRUD: Student
    # ----------------------------------------------------------------------
    def student_list(self, limit=50, offset=0):
        with self._session() as s:
            res = s.execute(
                select(Student).order_by(Student.student_id).limit(limit).offset(offset)
            ).scalars().all()
            return [
                {
                    "student_id": st.student_id,
                    "last_name":  st.last_name,
                    "first_name": st.first_name,
                    "email":      st.email,
                    "group_code": st.group_code,
                } for st in res
            ]

    def student_get(self, student_id: int):
        with self._session() as s:
            st = s.get(Student, student_id)
            if not st:
                return None
            return {
                "student_id": st.student_id,
                "last_name":  st.last_name,
                "first_name": st.first_name,
                "email":      st.email,
                "group_code": st.group_code,
            }

    def student_create(self, last_name: str, first_name: str, email: str, group_code: str) -> int:
        with self._session() as s:
            st = Student(last_name=last_name, first_name=first_name, email=email, group_code=group_code)
            s.add(st)
            s.flush()  # отримати PK
            return st.student_id

    def student_update(self, student_id: int, last_name: str, first_name: str, email: str, group_code: str) -> int:
        with self._session() as s:
            st = s.get(Student, student_id)
            if not st:
                return 0
            st.last_name = last_name
            st.first_name = first_name
            st.email = email
            st.group_code = group_code
            return 1

    def student_delete(self, student_id: int) -> int:
        with self._session() as s:
            st = s.get(Student, student_id)
            if not st:
                return 0
            s.delete(st)
            return 1

    def count_enrollments_by_student(self, student_id: int) -> int:
        with self._session() as s:
            return s.scalar(
                select(func.count()).select_from(Enrollment).where(Enrollment.student_id == student_id)
            )

    # ----------------------------------------------------------------------
    # CRUD: Instructor
    # ----------------------------------------------------------------------
    def instructor_list(self, limit=50, offset=0):
        with self._session() as s:
            res = s.execute(
                select(Instructor).order_by(Instructor.instructor_id).limit(limit).offset(offset)
            ).scalars().all()
            return [
                {
                    "instructor_id": it.instructor_id,
                    "last_name":     it.last_name,
                    "first_name":    it.first_name,
                    "email":         it.email,
                    "department":    it.department,
                } for it in res
            ]

    def instructor_get(self, instructor_id: int):
        with self._session() as s:
            it = s.get(Instructor, instructor_id)
            if not it:
                return None
            return {
                "instructor_id": it.instructor_id,
                "last_name":     it.last_name,
                "first_name":    it.first_name,
                "email":         it.email,
                "department":    it.department,
            }

    def instructor_create(self, last_name: str, first_name: str, email: str, department: str) -> int:
        with self._session() as s:
            it = Instructor(last_name=last_name, first_name=first_name, email=email, department=department)
            s.add(it)
            s.flush()
            return it.instructor_id

    def instructor_update(self, instructor_id: int, last_name: str, first_name: str, email: str, department: str) -> int:
        with self._session() as s:
            it = s.get(Instructor, instructor_id)
            if not it:
                return 0
            it.last_name = last_name
            it.first_name = first_name
            it.email = email
            it.department = department
            return 1

    def instructor_delete(self, instructor_id: int) -> int:
        with self._session() as s:
            it = s.get(Instructor, instructor_id)
            if not it:
                return 0
            s.delete(it)
            return 1

    def count_enrollments_by_instructor(self, instructor_id: int) -> int:
        with self._session() as s:
            return s.scalar(
                select(func.count()).select_from(Enrollment).where(Enrollment.instructor_id == instructor_id)
            )

    # ----------------------------------------------------------------------
    # CRUD: Course
    # ----------------------------------------------------------------------
    def course_list(self, limit=50, offset=0):
        with self._session() as s:
            res = s.execute(
                select(Course).order_by(Course.course_id).limit(limit).offset(offset)
            ).scalars().all()
            return [
                {
                    "course_id": c.course_id,
                    "title":     c.title,
                    "credits":   c.credits,
                    "semester":  c.semester,
                } for c in res
            ]

    def course_get(self, course_id: int):
        with self._session() as s:
            c = s.get(Course, course_id)
            if not c:
                return None
            return {
                "course_id": c.course_id,
                "title":     c.title,
                "credits":   c.credits,
                "semester":  c.semester,
            }

    def course_create(self, title: str, credits: int, semester: int) -> int:
        with self._session() as s:
            c = Course(title=title, credits=credits, semester=semester)
            s.add(c)
            s.flush()
            return c.course_id

    def course_update(self, course_id: int, title: str, credits: int, semester: int) -> int:
        with self._session() as s:
            c = s.get(Course, course_id)
            if not c:
                return 0
            c.title = title
            c.credits = credits
            c.semester = semester
            return 1

    def course_delete(self, course_id: int) -> int:
        with self._session() as s:
            c = s.get(Course, course_id)
            if not c:
                return 0
            s.delete(c)
            return 1

    def count_enrollments_by_course(self, course_id: int) -> int:
        with self._session() as s:
            return s.scalar(
                select(func.count()).select_from(Enrollment).where(Enrollment.course_id == course_id)
            )

    # ----------------------------------------------------------------------
    # CRUD: Enrollment (PK: course_id, student_id, instructor_id)
    # ----------------------------------------------------------------------
    def enrollment_list(self, limit=50, offset=0):
        with self._session() as s:
            q = (
                select(
                    Enrollment.course_id,
                    Course.title,
                    Enrollment.student_id,
                    Student.last_name.label("s_last"),
                    Student.first_name.label("s_first"),
                    Enrollment.instructor_id,
                    Instructor.last_name.label("i_last"),
                    Instructor.first_name.label("i_first"),
                )
                .join(Course, Course.course_id == Enrollment.course_id)
                .join(Student, Student.student_id == Enrollment.student_id)
                .join(Instructor, Instructor.instructor_id == Enrollment.instructor_id)
                .order_by(Enrollment.course_id, Enrollment.student_id, Enrollment.instructor_id)
                .limit(limit).offset(offset)
            )
            rows = s.execute(q).all()
            return [dict(r._mapping) for r in rows]

    def enrollment_exists(self, course_id: int, student_id: int, instructor_id: int) -> bool:
        with self._session() as s:
            return s.get(Enrollment, (course_id, student_id, instructor_id)) is not None

    def enrollment_create(self, course_id: int, student_id: int, instructor_id: int) -> int:
        with self._session() as s:
            if s.get(Enrollment, (course_id, student_id, instructor_id)):
                return 0
            en = Enrollment(course_id=course_id, student_id=student_id, instructor_id=instructor_id)
            s.add(en)
            return 1

    def enrollment_delete(self, course_id: int, student_id: int, instructor_id: int) -> int:
        with self._session() as s:
            en = s.get(Enrollment, (course_id, student_id, instructor_id))
            if not en:
                return 0
            s.delete(en)
            return 1

    def count_exams_for_enrollment(self, course_id: int, student_id: int, instructor_id: int) -> int:
        with self._session() as s:
            return s.scalar(
                select(func.count()).select_from(Exam).where(
                    Exam.course_id == course_id,
                    Exam.student_id == student_id,
                    Exam.instructor_id == instructor_id,
                )
            )

    # ----------------------------------------------------------------------
    # CRUD: Exam (PK: student_id, course_id, instructor_id, attempt_no)
    # ----------------------------------------------------------------------
    def exam_list(self, limit=50, offset=0):
        with self._session() as s:
            q = (
                select(
                    Exam.student_id,
                    Student.last_name.label("s_last"),
                    Student.first_name.label("s_first"),
                    Exam.course_id,
                    Course.title,
                    Exam.instructor_id,
                    Instructor.last_name.label("i_last"),
                    Instructor.first_name.label("i_first"),
                    Exam.attempt_no,
                    Exam.document,
                    Exam.exam_date,
                    Exam.grade,
                )
                .join(Student, Student.student_id == Exam.student_id)
                .join(Course, Course.course_id == Exam.course_id)
                .join(Instructor, Instructor.instructor_id == Exam.instructor_id)
                .order_by(Exam.exam_date.desc())
                .limit(limit).offset(offset)
            )
            rows = s.execute(q).all()
            return [dict(r._mapping) for r in rows]

    def exam_create(
        self, student_id: int, course_id: int, instructor_id: int,
        attempt_no: int, document: str, exam_date: str, grade: int
    ) -> int:
        with self._session() as s:
            ex = Exam(
                student_id=student_id, course_id=course_id, instructor_id=instructor_id,
                attempt_no=attempt_no, document=document, exam_date=exam_date, grade=grade
            )
            s.add(ex)
            return 1

    def exam_delete(self, student_id: int, course_id: int, instructor_id: int, attempt_no: int) -> int:
        with self._session() as s:
            ex = s.get(Exam, (student_id, course_id, instructor_id, attempt_no))
            if not ex:
                return 0
            s.delete(ex)
            return 1

    def exam_get_next_attempt(self, student_id: int, course_id: int, instructor_id: int) -> int:
        with self._session() as s:
            return s.scalar(
                select(func.coalesce(func.max(Exam.attempt_no), 0) + 1).where(
                    Exam.student_id == student_id,
                    Exam.course_id == course_id,
                    Exam.instructor_id == instructor_id,
                )
            )

    def exam_update(
        self, student_id: int, course_id: int, instructor_id: int, attempt_no: int,
        document: str, exam_date: str, grade: int
    ) -> int:
        with self._session() as s:
            ex = s.get(Exam, (student_id, course_id, instructor_id, attempt_no))
            if not ex:
                return 0
            ex.document = document
            ex.exam_date = exam_date
            ex.grade = grade
            return 1

    # ----------------------------------------------------------------------
    # Генерація даних (через SQLAlchemy Core + PostgreSQL-функції)
    # Повертаємо кількість доданих рядків
    # ----------------------------------------------------------------------
    def generate_students(self, n: int) -> int:
        sql = """
        INSERT INTO public."Student"(last_name, first_name, email, group_code)
        SELECT
          'Last_' || gs::text,
          'First_' || gs::text,
          'student_' || gs::text || '@example.edu',
          'KP-' || (10 + (random()*20)::int)::text
        FROM generate_series(1, :n) AS gs
        ON CONFLICT (email) DO NOTHING;
        """
        with self._session() as s:
            res = s.execute(text(sql), {"n": n})
            # rowcount може повертати 0 при ON CONFLICT DO NOTHING для дубліката
            return res.rowcount if res.rowcount is not None else 0

    def generate_instructors(self, n: int) -> int:
        m = max(1, n // 100)
        sql = """
        INSERT INTO public."Instructor"(last_name, first_name, email, department)
        SELECT
          'InstrL_' || gs::text,
          'InstrF_' || gs::text,
          'instructor_' || gs::text || '@univ.edu',
          'Dept_' || (1 + (random()*10)::int)::text
        FROM generate_series(1, :m) AS gs
        ON CONFLICT (email) DO NOTHING;
        """
        with self._session() as s:
            res = s.execute(text(sql), {"m": m})
            return res.rowcount if res.rowcount is not None else 0

    def generate_courses(self) -> int:
        sql = """
        INSERT INTO public."Course"(title, credits, semester)
        SELECT t,
               (1 + (random()*5)::int)::smallint,
               (1 + (random()*8)::int)::smallint
        FROM unnest(ARRAY[
            'Databases','Algorithms','Discrete Math','Networks',
            'OS','AI','ML','SE','Web'
        ]) AS t
        ON CONFLICT DO NOTHING;
        """
        with self._session() as s:
            res = s.execute(text(sql))
            return res.rowcount if res.rowcount is not None else 0

    def generate_enrollments(self, n: int) -> int:
        sql = """
        WITH s AS (SELECT student_id FROM public."Student" ORDER BY random() LIMIT GREATEST(1, :n/2)),
             c AS (SELECT course_id  FROM public."Course"  ORDER BY random() LIMIT 10),
             i AS (SELECT instructor_id FROM public."Instructor" ORDER BY random() LIMIT 20)
        INSERT INTO public."Enrollment"(course_id, student_id, instructor_id)
        SELECT c.course_id, s.student_id, i.instructor_id
        FROM s CROSS JOIN c CROSS JOIN i
        ON CONFLICT DO NOTHING;
        """
        with self._session() as s:
            res = s.execute(text(sql), {"n": n})
            return res.rowcount if res.rowcount is not None else 0

    def generate_exams(self, n: int) -> int:
        sql = """
        WITH e AS (
          SELECT course_id, student_id, instructor_id
          FROM public."Enrollment"
          ORDER BY random()
          LIMIT :n
        ),
        attempts AS (
          SELECT
            e.course_id,
            e.student_id,
            e.instructor_id,
            gs AS attempt_no
          FROM e
          JOIN generate_series(1, 3) AS gs ON TRUE
        )
        INSERT INTO public."Exam"(
            student_id,
            course_id,
            instructor_id,
            attempt_no,
            document,
            exam_date,
            grade
        )
        SELECT
          student_id,
          course_id,
          instructor_id,
          attempt_no,
          'doc_' || md5(random()::text)                                  AS document,
          (CURRENT_DATE - ((random()*365)::int))::date                   AS exam_date,
          ((random()*100)::int)::smallint                                AS grade
        FROM attempts
        ON CONFLICT DO NOTHING;
        """
        with self._session() as s:
            res = s.execute(text(sql), {"n": n})
            return res.rowcount if res.rowcount is not None else 0

    # ----------------------------------------------------------------------
    # СКЛАДНІ ПОШУКИ (через ORM/SQLAlchemy Core)
    # Повернення — список словників
    # ----------------------------------------------------------------------
    def search_1(
        self, group_code: str, grade_min: int, grade_max: int,
        course_title_pattern: str, date_from: str, date_to: str
    ):
        with self._session() as s:
            q = (
                select(
                    Student.student_id,
                    Student.last_name,
                    Student.first_name,
                    Course.title,
                    Exam.attempt_no,
                    Exam.exam_date,
                    Exam.grade,
                )
                .join(Enrollment, and_(
                    Enrollment.student_id == Exam.student_id,
                    Enrollment.course_id == Exam.course_id,
                    Enrollment.instructor_id == Exam.instructor_id,
                ))
                .join(Student, Student.student_id == Exam.student_id)
                .join(Course, Course.course_id == Exam.course_id)
                .where(
                    Student.group_code == group_code,
                    Exam.grade.between(grade_min, grade_max),
                    Course.title.ilike(course_title_pattern),
                    Exam.exam_date.between(date_from, date_to),
                )
                .order_by(Student.last_name, Student.first_name, Exam.exam_date.desc())
            )
            rows = s.execute(q).all()
            return [dict(r._mapping) for r in rows]

    def search_2(self, date_from: str, date_to: str, min_attempts: int):
        with self._session() as s:
            instructor_fullname = (Instructor.last_name + literal_column("' '") + Instructor.first_name).label("instructor")
            q = (
                select(
                    Course.title,
                    instructor_fullname,
                    func.count().label("attempts"),
                    func.round(func.avg(Exam.grade), 1).label("avg_grade"),
                )
                .join(Enrollment, and_(
                    Enrollment.student_id == Exam.student_id,
                    Enrollment.course_id == Exam.course_id,
                    Enrollment.instructor_id == Exam.instructor_id,
                ))
                .join(Course, Course.course_id == Exam.course_id)
                .join(Instructor, Instructor.instructor_id == Exam.instructor_id)
                .where(Exam.exam_date.between(date_from, date_to))
                .group_by(Course.title, Instructor.last_name, Instructor.first_name)
                .having(func.count() >= min_attempts)
                .order_by(literal_column("avg_grade").desc())
            )
            rows = s.execute(q).all()
            return [dict(r._mapping) for r in rows]

    def search_3(self, semester: int, min_credits: int, fail_threshold: int):
        # Остання спроба за (student, course, instructor) за датою/attempt_no — вікно row_number()
        with self._session() as s:
            la = (
                select(
                    Exam.student_id,
                    Exam.course_id,
                    Exam.instructor_id,
                    Exam.attempt_no,
                    Exam.document,
                    Exam.exam_date,
                    Exam.grade,
                    func.row_number()
                    .over(
                        partition_by=(Exam.student_id, Exam.course_id, Exam.instructor_id),
                        order_by=(Exam.exam_date.desc(), Exam.attempt_no.desc()),
                    )
                    .label("rn"),
                )
            ).subquery("last_attempt")

            q = (
                select(
                    Student.student_id,
                    Student.last_name,
                    Student.first_name,
                    Course.title,
                    Course.semester,
                    Course.credits,
                    la.c.grade.label("last_grade"),
                    la.c.exam_date.label("last_exam_date"),
                )
                .join(Enrollment, and_(
                    Enrollment.student_id == la.c.student_id,
                    Enrollment.course_id == la.c.course_id,
                    Enrollment.instructor_id == la.c.instructor_id,
                ))
                .join(Student, Student.student_id == la.c.student_id)
                .join(Course, Course.course_id == la.c.course_id)
                .where(
                    la.c.rn == 1,
                    Course.semester == semester,
                    Course.credits >= min_credits,
                    la.c.grade < fail_threshold,
                )
                .order_by(literal_column("last_grade").asc(), literal_column("last_exam_date").desc())
            )
            rows = s.execute(q).all()
            return [dict(r._mapping) for r in rows]
