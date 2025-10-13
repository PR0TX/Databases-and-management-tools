# model.py
# Увесь доступ до БД

import psycopg
from psycopg.rows import dict_row

class Model:
    def __init__(self, dsn: str):
        self._dsn = dsn

    def _conn(self):
        # row_factory=dict_row -> отримуємо dict-рядки  
        return psycopg.connect(self._dsn, row_factory=dict_row)

    def ping(self) -> bool:
        try:
            with self._conn() as conn, conn.cursor() as cur:
                cur.execute("SELECT 1;")
                cur.fetchone()
            return True
        except psycopg.Error:
            return False

    # ---------------------------
    # CRUD: Student
    # ---------------------------
    def student_list(self, limit=50, offset=0):
        with self._conn() as conn, conn.cursor() as cur:
            cur.execute(
                """SELECT student_id, last_name, first_name, email, group_code
                   FROM "Student" ORDER BY student_id
                   LIMIT %s OFFSET %s;""",
                (limit, offset),
            )
            return cur.fetchall()

    def student_get(self, student_id:int):
        with self._conn() as conn, conn.cursor() as cur:
            cur.execute(
                """SELECT student_id, last_name, first_name, email, group_code
                   FROM "Student" WHERE student_id=%s;""",
                (student_id,),
            )
            return cur.fetchone()

    def student_create(self, last_name:str, first_name:str, email:str, group_code:str) -> int:
        with self._conn() as conn, conn.cursor() as cur:
            cur.execute(
                """INSERT INTO "Student"(last_name, first_name, email, group_code)
                   VALUES (%s,%s,%s,%s) RETURNING student_id;""",
                (last_name, first_name, email, group_code),
            )
            new_id = cur.fetchone()["student_id"]
            conn.commit()
            return new_id

    def student_update(self, student_id:int, last_name:str, first_name:str, email:str, group_code:str) -> int:
        with self._conn() as conn, conn.cursor() as cur:
            cur.execute(
                """UPDATE "Student"
                   SET last_name=%s, first_name=%s, email=%s, group_code=%s
                   WHERE student_id=%s;""",
                (last_name, first_name, email, group_code, student_id),
            )
            conn.commit()
            return cur.rowcount

    def student_delete(self, student_id:int) -> int:
        with self._conn() as conn, conn.cursor() as cur:
            cur.execute("""DELETE FROM "Student" WHERE student_id=%s;""", (student_id,))
            conn.commit()
            return cur.rowcount

    def count_enrollments_by_student(self, student_id:int) -> int:
        with self._conn() as conn, conn.cursor() as cur:
            cur.execute("""SELECT COUNT(*) AS cnt FROM "Enrollment" WHERE student_id=%s;""", (student_id,))
            return cur.fetchone()["cnt"]

    # ---------------------------
    # CRUD: Instructor
    # ---------------------------
    def instructor_list(self, limit=50, offset=0):
        with self._conn() as conn, conn.cursor() as cur:
            cur.execute(
                """SELECT instructor_id, last_name, first_name, email, department
                   FROM "Instructor" ORDER BY instructor_id
                   LIMIT %s OFFSET %s;""",
                (limit, offset),
            )
            return cur.fetchall()

    def instructor_get(self, instructor_id:int):
        with self._conn() as conn, conn.cursor() as cur:
            cur.execute(
                """SELECT instructor_id, last_name, first_name, email, department
                   FROM "Instructor" WHERE instructor_id=%s;""",
                (instructor_id,),
            )
            return cur.fetchone()

    def instructor_create(self, last_name:str, first_name:str, email:str, department:str) -> int:
        with self._conn() as conn, conn.cursor() as cur:
            cur.execute(
                """INSERT INTO "Instructor"(last_name, first_name, email, department)
                   VALUES (%s,%s,%s,%s) RETURNING instructor_id;""",
                (last_name, first_name, email, department),
            )
            new_id = cur.fetchone()["instructor_id"]
            conn.commit()
            return new_id

    def instructor_update(self, instructor_id:int, last_name:str, first_name:str, email:str, department:str) -> int:
        with self._conn() as conn, conn.cursor() as cur:
            cur.execute(
                """UPDATE "Instructor"
                   SET last_name=%s, first_name=%s, email=%s, department=%s
                   WHERE instructor_id=%s;""",
                (last_name, first_name, email, department, instructor_id),
            )
            conn.commit()
            return cur.rowcount

    def instructor_delete(self, instructor_id:int) -> int:
        with self._conn() as conn, conn.cursor() as cur:
            cur.execute("""DELETE FROM "Instructor" WHERE instructor_id=%s;""", (instructor_id,))
            conn.commit()
            return cur.rowcount

    def count_enrollments_by_instructor(self, instructor_id:int) -> int:
        with self._conn() as conn, conn.cursor() as cur:
            cur.execute("""SELECT COUNT(*) AS cnt FROM "Enrollment" WHERE instructor_id=%s;""", (instructor_id,))
            return cur.fetchone()["cnt"]

    # ---------------------------
    # CRUD: Course
    # ---------------------------
    def course_list(self, limit=50, offset=0):
        with self._conn() as conn, conn.cursor() as cur:
            cur.execute(
                """SELECT course_id, title, credits, semester
                   FROM "Course" ORDER BY course_id
                   LIMIT %s OFFSET %s;""",
                (limit, offset),
            )
            return cur.fetchall()

    def course_get(self, course_id:int):
        with self._conn() as conn, conn.cursor() as cur:
            cur.execute(
                """SELECT course_id, title, credits, semester
                   FROM "Course" WHERE course_id=%s;""",
                (course_id,),
            )
            return cur.fetchone()

    def course_create(self, title:str, credits:int, semester:int) -> int:
        with self._conn() as conn, conn.cursor() as cur:
            cur.execute(
                """INSERT INTO "Course"(title, credits, semester)
                   VALUES (%s,%s,%s) RETURNING course_id;""",
                (title, credits, semester),
            )
            new_id = cur.fetchone()["course_id"]
            conn.commit()
            return new_id

    def course_update(self, course_id:int, title:str, credits:int, semester:int) -> int:
        with self._conn() as conn, conn.cursor() as cur:
            cur.execute(
                """UPDATE "Course"
                   SET title=%s, credits=%s, semester=%s
                   WHERE course_id=%s;""",
                (title, credits, semester, course_id),
            )
            conn.commit()
            return cur.rowcount

    def course_delete(self, course_id:int) -> int:
        with self._conn() as conn, conn.cursor() as cur:
            cur.execute("""DELETE FROM "Course" WHERE course_id=%s;""", (course_id,))
            conn.commit()
            return cur.rowcount

    def count_enrollments_by_course(self, course_id:int) -> int:
        with self._conn() as conn, conn.cursor() as cur:
            cur.execute("""SELECT COUNT(*) AS cnt FROM "Enrollment" WHERE course_id=%s;""", (course_id,))
            return cur.fetchone()["cnt"]

    # ---------------------------
    # CRUD: Enrollment (PK: course_id, student_id, instructor_id)
    # ---------------------------
    def enrollment_list(self, limit=50, offset=0):
        with self._conn() as conn, conn.cursor() as cur:
            cur.execute(
                """SELECT en.course_id, c.title, en.student_id, s.last_name AS s_last, s.first_name AS s_first,
                          en.instructor_id, i.last_name AS i_last, i.first_name AS i_first
                   FROM "Enrollment" en
                   JOIN "Course" c ON c.course_id=en.course_id
                   JOIN "Student" s ON s.student_id=en.student_id
                   JOIN "Instructor" i ON i.instructor_id=en.instructor_id
                   ORDER BY en.course_id, en.student_id, en.instructor_id
                   LIMIT %s OFFSET %s;""",
                (limit, offset),
            )
            return cur.fetchall()

    def enrollment_exists(self, course_id:int, student_id:int, instructor_id:int) -> bool:
        with self._conn() as conn, conn.cursor() as cur:
            cur.execute(
                """SELECT 1 FROM "Enrollment"
                   WHERE course_id=%s AND student_id=%s AND instructor_id=%s;""",
                (course_id, student_id, instructor_id),
            )
            return cur.fetchone() is not None

    def enrollment_create(self, course_id:int, student_id:int, instructor_id:int) -> int:
        with self._conn() as conn, conn.cursor() as cur:
            cur.execute(
                """INSERT INTO "Enrollment"(course_id, student_id, instructor_id)
                   VALUES (%s,%s,%s) ON CONFLICT DO NOTHING;""",
                (course_id, student_id, instructor_id),
            )
            conn.commit()
            return cur.rowcount  # 1 якщо додано, 0 якщо існує

    def enrollment_delete(self, course_id:int, student_id:int, instructor_id:int) -> int:
        with self._conn() as conn, conn.cursor() as cur:
            cur.execute(
                """DELETE FROM "Enrollment"
                   WHERE course_id=%s AND student_id=%s AND instructor_id=%s;""",
                (course_id, student_id, instructor_id),
            )
            conn.commit()
            return cur.rowcount

    def count_exams_for_enrollment(self, course_id:int, student_id:int, instructor_id:int) -> int:
        with self._conn() as conn, conn.cursor() as cur:
            cur.execute(
                """SELECT COUNT(*) AS cnt FROM "Exam"
                   WHERE course_id=%s AND student_id=%s AND instructor_id=%s;""",
                (course_id, student_id, instructor_id),
            )
            return cur.fetchone()["cnt"]

    # ---------------------------
    # CRUD: Exam (PK: student_id, course_id, instructor_id, attempt_no)
    # ---------------------------
    def exam_list(self, limit=50, offset=0):
        with self._conn() as conn, conn.cursor() as cur:
            cur.execute(
                """SELECT ex.student_id, s.last_name AS s_last, s.first_name AS s_first,
                          ex.course_id, c.title,
                          ex.instructor_id, i.last_name AS i_last, i.first_name AS i_first,
                          ex.attempt_no, ex.document, ex.exam_date, ex.grade
                   FROM "Exam" ex
                   JOIN "Student" s ON s.student_id=ex.student_id
                   JOIN "Course"  c ON c.course_id=ex.course_id
                   JOIN "Instructor" i ON i.instructor_id=ex.instructor_id
                   ORDER BY ex.exam_date DESC
                   LIMIT %s OFFSET %s;""",
                (limit, offset),
            )
            return cur.fetchall()

    def exam_create(self, student_id:int, course_id:int, instructor_id:int,
                    attempt_no:int, document:str, exam_date:str, grade:int) -> int:
        with self._conn() as conn, conn.cursor() as cur:
            cur.execute(
                """INSERT INTO "Exam"(student_id, course_id, instructor_id, attempt_no, document, exam_date, grade)
                   VALUES (%s,%s,%s,%s,%s,%s,%s);""",
                (student_id, course_id, instructor_id, attempt_no, document, exam_date, grade),
            )
            conn.commit()
            return cur.rowcount

    def exam_delete(self, student_id:int, course_id:int, instructor_id:int, attempt_no:int) -> int:
        with self._conn() as conn, conn.cursor() as cur:
            cur.execute(
                """DELETE FROM "Exam"
                   WHERE student_id=%s AND course_id=%s AND instructor_id=%s AND attempt_no=%s;""",
                (student_id, course_id, instructor_id, attempt_no),
            )
            conn.commit()
            return cur.rowcount

    def exam_get_next_attempt(self, student_id:int, course_id:int, instructor_id:int) -> int:
        with self._conn() as conn, conn.cursor() as cur:
            cur.execute(
                """SELECT COALESCE(MAX(attempt_no),0)+1 AS next_no
                   FROM "Exam"
                   WHERE student_id=%s AND course_id=%s AND instructor_id=%s;""",
                (student_id, course_id, instructor_id),
            )
            return cur.fetchone()["next_no"]
    def exam_update(self, student_id:int, course_id:int, instructor_id:int, attempt_no:int,
                    document:str, exam_date:str, grade:int) -> int:
        with self._conn() as conn, conn.cursor() as cur:
            cur.execute(
                '''UPDATE "Exam"
                   SET document=%s, exam_date=%s, grade=%s
                   WHERE student_id=%s AND course_id=%s AND instructor_id=%s AND attempt_no=%s;''',
                (document, exam_date, grade, student_id, course_id, instructor_id, attempt_no),
            )
            conn.commit()
            return cur.rowcount


    # ---------------------------
    # Генерація даних (SQL)
    # ---------------------------
    def generate_students(self, n:int) -> int:
        sql = """
        INSERT INTO "Student"(last_name, first_name, email, group_code)
        SELECT 
          'Last_' || gs::text,
          'First_' || gs::text,
          'student_' || gs::text || '@example.edu',
          'KP-' || (10 + (random()*20)::int)::text
        FROM generate_series(1, %s) AS gs;
        ON CONFLICT (email) DO NOTHING;
        """
        with self._conn() as conn, conn.cursor() as cur:
            cur.execute(sql, (n,))
            conn.commit()
            return cur.rowcount

    def generate_instructors(self, n:int) -> int:
        m = max(1, n // 100)
        sql = """
        INSERT INTO "Instructor"(last_name, first_name, email, department)
        SELECT 
          'InstrL_' || gs::text,
          'InstrF_' || gs::text,
          'instructor_' || gs::text || '@univ.edu',
          'Dept_' || (1 + (random()*10)::int)::text
        FROM generate_series(1, %s) AS gs;
        ON CONFLICT (email) DO NOTHING;
        """
        with self._conn() as conn, conn.cursor() as cur:
            cur.execute(sql, (m,))
            conn.commit()
            return cur.rowcount

    def generate_courses(self) -> int:
        sql = """
        INSERT INTO "Course"(title, credits, semester)
        SELECT t,
               (1 + (random()*5)::int)::smallint,
               (1 + (random()*8)::int)::smallint
        FROM unnest(ARRAY[
            'Databases','Algorithms','Discrete Math','Networks',
            'OS','AI','ML','SE','Web'
        ]) AS t;
        """
        with self._conn() as conn, conn.cursor() as cur:
            cur.execute(sql)
            conn.commit()
            return cur.rowcount

    def generate_enrollments(self, n:int) -> int:
        sql = """
        WITH s AS (SELECT student_id FROM "Student" ORDER BY random() LIMIT GREATEST(1, %s/2)),
             c AS (SELECT course_id  FROM "Course"  ORDER BY random() LIMIT 10),
             i AS (SELECT instructor_id FROM "Instructor" ORDER BY random() LIMIT 20)
        INSERT INTO "Enrollment"(course_id, student_id, instructor_id)
        SELECT c.course_id, s.student_id, i.instructor_id
        FROM s CROSS JOIN c CROSS JOIN i
        ON CONFLICT DO NOTHING;
        """
        with self._conn() as conn, conn.cursor() as cur:
            cur.execute(sql, (n,))
            conn.commit()
            return cur.rowcount

    def generate_exams(self, n:int) -> int:
        sql = """
        WITH e AS (
          SELECT course_id, student_id, instructor_id
          FROM "Enrollment"
          ORDER BY random()
          LIMIT %s
        ),
        attempts AS (
          SELECT e.*, gs AS attempt_no
          FROM e
          JOIN generate_series(1, (1 + (random()*3)::int)) AS gs ON TRUE
        )
        INSERT INTO "Exam"(student_id, course_id, instructor_id, attempt_no, document, exam_date, grade)
        SELECT 
          student_id, course_id, instructor_id, attempt_no,
          'doc_' || md5(random()::text),
          CURRENT_DATE - ((random()*1095)::int)
          (random()*101)::int
        FROM attempts
        ON CONFLICT DO NOTHING;
        """
        with self._conn() as conn, conn.cursor() as cur:
            cur.execute(sql, (n,))
            conn.commit()
            return cur.rowcount

    # ---------------------------
    # СКЛАДНІ ПОШУКИ 
    # ---------------------------
    def search_1(self, group_code:str, grade_min:int, grade_max:int,
                 course_title_pattern:str, date_from:str, date_to:str):
        sql = """
        SELECT s.student_id, s.last_name, s.first_name, c.title,
               ex.attempt_no, ex.exam_date, ex.grade
        FROM "Exam" ex
        JOIN "Enrollment" en USING (student_id, course_id, instructor_id)
        JOIN "Student" s ON s.student_id = ex.student_id
        JOIN "Course"  c ON c.course_id  = ex.course_id
        WHERE s.group_code = %s
          AND ex.grade BETWEEN %s AND %s
          AND c.title ILIKE %s
          AND ex.exam_date BETWEEN %s AND %s
        ORDER BY s.last_name, s.first_name, ex.exam_date DESC;
        """
        with self._conn() as conn, conn.cursor() as cur:
            cur.execute(sql, (group_code, grade_min, grade_max,
                              course_title_pattern, date_from, date_to))
            return cur.fetchall()

    def search_2(self, date_from:str, date_to:str, min_attempts:int):
        sql = """
        SELECT c.title,
               i.last_name || ' ' || i.first_name AS instructor,
               COUNT(*)               AS attempts,
               ROUND(AVG(ex.grade),1) AS avg_grade
        FROM "Exam" ex
        JOIN "Enrollment" en USING (student_id, course_id, instructor_id)
        JOIN "Course"  c ON c.course_id = ex.course_id
        JOIN "Instructor" i ON i.instructor_id = ex.instructor_id
        WHERE ex.exam_date BETWEEN %s AND %s
        GROUP BY c.title, i.last_name, i.first_name
        HAVING COUNT(*) >= %s
        ORDER BY avg_grade DESC;
        """
        with self._conn() as conn, conn.cursor() as cur:
            cur.execute(sql, (date_from, date_to, min_attempts))
            return cur.fetchall()

    def search_3(self, semester:int, min_credits:int, fail_threshold:int):
        # (враховуємо, що студент міг перескласти, тому беремо останню спробу)
        sql = """
        WITH last_attempt AS (
            SELECT
                ex.student_id, ex.course_id, ex.instructor_id,
                ex.attempt_no, ex.document, ex.exam_date, ex.grade,
                ROW_NUMBER() OVER (
                    PARTITION BY ex.student_id, ex.course_id, ex.instructor_id
                    ORDER BY ex.exam_date DESC, ex.attempt_no DESC
                ) AS rn
            FROM "Exam" ex
        )
        SELECT
            s.student_id, s.last_name, s.first_name,
            c.title, c.semester, c.credits,
            la.grade AS last_grade,
            la.exam_date AS last_exam_date
        FROM last_attempt la
        JOIN "Enrollment" en
        ON en.student_id = la.student_id
        AND en.course_id  = la.course_id
        AND en.instructor_id = la.instructor_id
        JOIN "Student" s ON s.student_id = la.student_id
        JOIN "Course"  c ON c.course_id  = la.course_id
        WHERE la.rn = 1
        AND c.semester = %s
        AND c.credits  >= %s
        AND la.grade   < %s
        ORDER BY last_grade ASC, last_exam_date DESC;
        """
        with self._conn() as conn, conn.cursor() as cur:
            cur.execute(sql, (semester, min_credits, fail_threshold))
            return cur.fetchall()

