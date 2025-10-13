# controller.py
# Бізнес-логіка, валідація, «контроль 1:N» (заборона delete батьківських при наявності дочірніх),
# заміри часу запитів, повідомлення.

import time
import psycopg
from model import Model
from view import View

class Controller:
    def __init__(self, model:Model, view:View):
        self.m = model
        self.v = view

    # ---------------------------
    # Головний цикл
    # ---------------------------
    def run(self):
        if not self.m.ping():
            self.v.err("Неможливо підключитися до БД. Перевір .env та доступність PostgreSQL.")
            return
        self.v.info("Підключення до БД виконано успішно.")

        while True:
            ch = self.v.main_menu()
            try:
                if ch == "1": self.menu_student()
                elif ch == "2": self.menu_instructor()
                elif ch == "3": self.menu_course()
                elif ch == "4": self.menu_enrollment()
                elif ch == "5": self.menu_exam()
                elif ch == "6": self.menu_generate()
                elif ch == "7": self.menu_searches()
                elif ch == "0": break
            except psycopg.errors.ForeignKeyViolation:
                self.v.err("Операцію відхилено: порушення зовнішнього ключа (foreign key).")
            except psycopg.errors.UniqueViolation:
                self.v.err("Операцію відхилено: порушення унікальності (наприклад, email вже існує).")
            except psycopg.Error as e:
                # Без системних трейcбеків: коротке службове пояснення
                self.v.err(f"Помилка БД (SQLSTATE={e.sqlstate}). Операцію не виконано.")
            except Exception as e:
                self.v.err(f"Непередбачена помилка: {e}")

    # ---------------------------
    # Student
    # ---------------------------
    def menu_student(self):
        while True:
            ch = self.v.submenu_crud("Student")
            if ch == "1":
                rows = self.m.student_list()
                self.v.show_rows(rows)
            elif ch == "2":
                ln = self.v.ask_str("Прізвище: ")
                fn = self.v.ask_str("Ім'я: ")
                email = self.v.ask_str("Email: ")
                grp = self.v.ask_str("Група (напр. KP-21): ")
                sid = self.m.student_create(ln, fn, email, grp)
                self.v.info(f"Додано student_id={sid}")
            elif ch == "3":
                sid = self.v.ask_int("ID студента: ", 1)
                s = self.m.student_get(sid)
                if not s:
                    self.v.warn("Немає такого ID.")
                else:
                    ln = self.v.ask_str(f"Прізвище [{s['last_name']}]: ", allow_empty=True) or s['last_name']
                    fn = self.v.ask_str(f"Ім'я [{s['first_name']}]: ", allow_empty=True) or s['first_name']
                    em = self.v.ask_str(f"Email [{s['email']}]: ", allow_empty=True) or s['email']
                    gc = self.v.ask_str(f"Група [{s['group_code']}]: ", allow_empty=True) or s['group_code']
                    cnt = self.m.student_update(sid, ln, fn, em, gc)
                    self.v.info(f"Оновлено рядків: {cnt}")
            elif ch == "4":
                sid = self.v.ask_int("ID студента для видалення: ", 1)
                # КОНТРОЛЬ 1:N: якщо є Enrollment — забороняємо видалення (незважаючи на CASCADE в БД)
                dep = self.m.count_enrollments_by_student(sid)
                if dep > 0:
                    self.v.err("Видалення заборонено: існують залежні рядки в Enrollment/Exam.")
                else:
                    cnt = self.m.student_delete(sid)
                    self.v.info(f"Видалено рядків: {cnt}")
            elif ch == "0":
                break

    # ---------------------------
    # Instructor
    # ---------------------------
    def menu_instructor(self):
        while True:
            ch = self.v.submenu_crud("Instructor")
            if ch == "1":
                rows = self.m.instructor_list()
                self.v.show_rows(rows)
            elif ch == "2":
                ln = self.v.ask_str("Прізвище: ")
                fn = self.v.ask_str("Ім'я: ")
                email = self.v.ask_str("Email: ")
                dep = self.v.ask_str("Кафедра/департамент: ")
                iid = self.m.instructor_create(ln, fn, email, dep)
                self.v.info(f"Додано instructor_id={iid}")
            elif ch == "3":
                iid = self.v.ask_int("ID викладача: ", 1)
                inst = self.m.instructor_get(iid)
                if not inst:
                    self.v.warn("Немає такого ID.")
                else:
                    ln = self.v.ask_str(f"Прізвище [{inst['last_name']}]: ", allow_empty=True) or inst['last_name']
                    fn = self.v.ask_str(f"Ім'я [{inst['first_name']}]: ", allow_empty=True) or inst['first_name']
                    em = self.v.ask_str(f"Email [{inst['email']}]: ", allow_empty=True) or inst['email']
                    dp = self.v.ask_str(f"Кафедра [{inst['department']}]: ", allow_empty=True) or inst['department']
                    cnt = self.m.instructor_update(iid, ln, fn, em, dp)
                    self.v.info(f"Оновлено рядків: {cnt}")
            elif ch == "4":
                iid = self.v.ask_int("ID викладача для видалення: ", 1)
                dep = self.m.count_enrollments_by_instructor(iid)
                if dep > 0:
                    self.v.err("Видалення заборонено: існують залежні рядки в Enrollment/Exam.")
                else:
                    cnt = self.m.instructor_delete(iid)
                    self.v.info(f"Видалено рядків: {cnt}")
            elif ch == "0":
                break

    # ---------------------------
    # Course
    # ---------------------------
    def menu_course(self):
        while True:
            ch = self.v.submenu_crud("Course")
            if ch == "1":
                rows = self.m.course_list()
                self.v.show_rows(rows)
            elif ch == "2":
                title = self.v.ask_str("Назва курсу: ")
                credits = self.v.ask_smallint("Кредити (smallint): ", 0, 32767)
                semester = self.v.ask_smallint("Семестр (smallint): ", 0, 32767)
                cid = self.m.course_create(title, credits, semester)
                self.v.info(f"Додано course_id={cid}")
            elif ch == "3":
                cid = self.v.ask_int("ID курсу: ", 1)
                c = self.m.course_get(cid)
                if not c:
                    self.v.warn("Немає такого ID.")
                else:
                    title = self.v.ask_str(f"Назва [{c['title']}]: ", allow_empty=True) or c['title']
                    credits = self.v.ask_smallint(f"Кредити [{c['credits']}]: ", 0, 32767)
                    semester = self.v.ask_smallint(f"Семестр [{c['semester']}]: ", 0, 32767)
                    cnt = self.m.course_update(cid, title, credits, semester)
                    self.v.info(f"Оновлено рядків: {cnt}")
            elif ch == "4":
                cid = self.v.ask_int("ID курсу для видалення: ", 1)
                dep = self.m.count_enrollments_by_course(cid)
                if dep > 0:
                    self.v.err("Видалення заборонено: існують залежні рядки в Enrollment/Exam.")
                else:
                    cnt = self.m.course_delete(cid)
                    self.v.info(f"Видалено рядків: {cnt}")
            elif ch == "0":
                break

    # ---------------------------
    # Enrollment
    # ---------------------------
    def menu_enrollment(self):
        while True:
            ch = self.v.submenu_crud("Enrollment (course_id, student_id, instructor_id)")
            if ch == "1":
                rows = self.m.enrollment_list()
                self.v.show_rows(rows)
            elif ch == "2":
                cid = self.v.ask_int("course_id: ", 1)
                sid = self.v.ask_int("student_id: ", 1)
                iid = self.v.ask_int("instructor_id: ", 1)
                # Перевіримо існування батьківських:
                if not self.m.course_get(cid):
                    self.v.err("Немає такого course_id.")
                    continue
                if not self.m.student_get(sid):
                    self.v.err("Немає такого student_id.")
                    continue
                if not self.m.instructor_get(iid):
                    self.v.err("Немає такого instructor_id.")
                    continue
                added = self.m.enrollment_create(cid, sid, iid)
                if added == 1:
                    self.v.info("Enrollment додано.")
                else:
                    self.v.warn("Така трійка вже існує.")
            elif ch == "3":
                self.v.warn("Оновлення Enrollment не застосовується (PK — трійка). Видаліть/створіть заново.")
            elif ch == "4":
                cid = self.v.ask_int("course_id: ", 1)
                sid = self.v.ask_int("student_id: ", 1)
                iid = self.v.ask_int("instructor_id: ", 1)
                # Контроль: якщо є Exam — забороняємо видалення
                dep = self.m.count_exams_for_enrollment(cid, sid, iid)
                if dep > 0:
                    self.v.err("Видалення заборонено: існують залежні 'Exam'.")
                else:
                    cnt = self.m.enrollment_delete(cid, sid, iid)
                    self.v.info(f"Видалено рядків: {cnt}")
            elif ch == "0":
                break

    # ---------------------------
    # Exam
    # ---------------------------
    def menu_exam(self):
        while True:
            ch = self.v.submenu_crud("Exam")
            if ch == "1":
                rows = self.m.exam_list()
                self.v.show_rows(rows)
            elif ch == "2":
                sid = self.v.ask_int("student_id: ", 1)
                cid = self.v.ask_int("course_id: ", 1)
                iid = self.v.ask_int("instructor_id: ", 1)
                # Перевірка наявності батьківської трійки
                if not self.m.enrollment_exists(cid, sid, iid):
                    self.v.err("Немає відповідної трійки в Enrollment. Спершу створіть Enrollment.")
                    continue
                # Пропонуємо авто-нумерацію спроб
                auto = self.v.confirm("Автоматично обрати наступний attempt_no?")
                if auto:
                    attempt_no = self.m.exam_get_next_attempt(sid, cid, iid)
                    self.v.info(f"Встановлено attempt_no={attempt_no}")
                else:
                    attempt_no = self.v.ask_smallint("attempt_no (smallint): ", 1)
                doc = self.v.ask_str("document (рядок/посилання): ")
                dt = self.v.ask_date_iso("exam_date (YYYY-MM-DD): ")
                grade = self.v.ask_smallint("grade (0..100): ", 0, 100)
                cnt = self.m.exam_create(sid, cid, iid, attempt_no, doc, dt, grade)
                self.v.info(f"Додано рядків: {cnt}")
            elif ch == "3":
                # ОНОВЛЕННЯ НЕключових полів (document/exam_date/grade)
                sid = self.v.ask_int("student_id: ", 1)
                cid = self.v.ask_int("course_id: ", 1)
                iid = self.v.ask_int("instructor_id: ", 1)
                at  = self.v.ask_smallint("attempt_no: ", 1)
                doc = self.v.ask_str("Новий document: ")
                dt  = self.v.ask_date_iso("Нова дата (YYYY-MM-DD): ")
                gr  = self.v.ask_smallint("Новий grade (0..100): ", 0, 100)
                cnt = self.m.exam_update(sid, cid, iid, at, doc, dt, gr)
                if cnt == 0:
                    self.v.warn("Рядок не знайдено або не змінено.")
                else:
                    self.v.info(f"Оновлено рядків: {cnt}")
            elif ch == "4":
                sid = self.v.ask_int("student_id: ", 1)
                cid = self.v.ask_int("course_id: ", 1)
                iid = self.v.ask_int("instructor_id: ", 1)
                at  = self.v.ask_smallint("attempt_no: ", 1)
                cnt = self.m.exam_delete(sid, cid, iid, at)
                self.v.info(f"Видалено рядків: {cnt}")
            elif ch == "0":
                break

    # ---------------------------
    # Генерація
    # ---------------------------
    def menu_generate(self):
        while True:
            ch = self.v.submenu_generate()
            try:
                if ch == "1":
                    n = self.v.ask_int("К-сть Student (напр. 100000): ", 1)
                    r = self.m.generate_students(n); self.v.info(f"Додано Student: {r}")
                elif ch == "2":
                    n = self.v.ask_int("Базове N (для ~N/100 викладачів): ", 1)
                    r = self.m.generate_instructors(n); self.v.info(f"Додано Instructor: {r}")
                elif ch == "3":
                    r = self.m.generate_courses(); self.v.info(f"Додано Course: {r}")
                elif ch == "4":
                    n = self.v.ask_int("Базове N (для масштабу Enrollment): ", 1)
                    r = self.m.generate_enrollments(n); self.v.info(f"Додано Enrollment: {r}")
                elif ch == "5":
                    n = self.v.ask_int("Базове N (скільки трійок взяти для Exam): ", 1)
                    r = self.m.generate_exams(n); self.v.info(f"Додано Exam: {r}")
                elif ch == "6":
                    # рекомендований конвеєр
                    n = self.v.ask_int("Базове N (напр. 100000): ", 1)
                    a = self.m.generate_students(n)
                    b = self.m.generate_instructors(n)
                    c = self.m.generate_courses()
                    d = self.m.generate_enrollments(n)
                    e = self.m.generate_exams(n)
                    self.v.info(f"OK: Student={a}, Instructor={b}, Course={c}, Enrollment={d}, Exam={e}")
                elif ch == "0":
                    break
            except psycopg.Error as e:
                self.v.err(f"Помилка генерації (SQLSTATE={e.sqlstate}).")

    # ---------------------------
    # Пошуки (3 запити) + час виконання (мс)
    # ---------------------------
    def timed(self, fn, *args):
        t0 = time.perf_counter()
        rows = fn(*args)
        ms = (time.perf_counter() - t0) * 1000.0
        return rows, ms

    def menu_searches(self):
        while True:
            ch = self.v.submenu_searches()
            if ch == "1":
                grp = self.v.ask_str("Група (напр. KP-21): ")
                gmin = self.v.ask_smallint("Мін. оцінка: ", 0, 100)
                gmax = self.v.ask_smallint("Макс. оцінка: ", 0, 100)
                patt = self.v.ask_like_pattern("Шаблон назви курсу (напр. DB або %Data%): ")
                d1 = self.v.ask_date_iso("Дата від (YYYY-MM-DD): ")
                d2 = self.v.ask_date_iso("Дата до  (YYYY-MM-DD): ")
                rows, ms = self.timed(self.m.search_1, grp, gmin, gmax, patt, d1, d2)
                self.v.show_rows(rows); self.v.info(f"Час виконання: {ms:.1f} мс")
            elif ch == "2":
                d1 = self.v.ask_date_iso("Дата від (YYYY-MM-DD): ")
                d2 = self.v.ask_date_iso("Дата до  (YYYY-MM-DD): ")
                min_att = self.v.ask_int("Мін. кількість спроб у групі: ", 1)
                rows, ms = self.timed(self.m.search_2, d1, d2, min_att)
                self.v.show_rows(rows); self.v.info(f"Час виконання: {ms:.1f} мс")
            elif ch == "3":
                sem = self.v.ask_smallint("Семестр: ", 0)
                credits = self.v.ask_smallint("Мін. кредити: ", 0)
                thr = self.v.ask_smallint("Поріг 'провалу' (наприклад 60): ", 0, 100)
                rows, ms = self.timed(self.m.search_3, sem, credits, thr)
                self.v.show_rows(rows); self.v.info(f"Час виконання: {ms:.1f} мс")
            elif ch == "0":
                break
