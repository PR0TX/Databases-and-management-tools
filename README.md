# РГР: Консольний застосунок для PostgreSQL (MVC, psycopg3)

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB.svg)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13%2B-336791.svg)](https://www.postgresql.org/)
[![psycopg3](https://img.shields.io/badge/Driver-psycopg3-0064a5.svg)](https://www.psycopg.org/)

Консольний застосунок для роботи з базою даних **обліку екзаменаційних балів студентів**.
Реалізовано **CRUD**, **масову генерацію «рандомізованих» даних** SQL-запитами та **3 параметризовані пошуки** з вимірюванням часу. Архітектура — **MVC** (окремі `model.py`, `view.py`, `controller.py`), взаємодія з БД — **SQL** (без ORM).

---

## Зміст

* [Мета](#мета)
* [Архітектура та структура проєкту](#архітектура-та-структура-проєкту)
* [Схема БД та ER-діаграма](#схема-бд-та-er-діаграма)
* [Встановлення та запуск](#встановлення-та-запуск)
* [Як користуватись (меню)](#як-користуватись-меню)
* [Генерація великих даних](#генерація-великих-даних)
* [Пошукові запити та вимір часу](#пошукові-запити-та-вимір-часу)
* [Обробка помилок та валідація](#обробка-помилок-та-валідація)
* [Контакти](#контакти)

---

## Мета

**Мета РГР:** здобути вміння програмування прикладних додатків БД PostgreSQL.

---

## Архітектура та структура проєкту

**Шаблон MVC**

* **Model (`model.py`)** — підключення, параметризовані SQL-запити, транзакції; повертає дані у зручному форматі (dict-рядки).
* **View (`view.py`)** — консольні меню/діалоги, валідація вводу (`int`, `smallint`, `date`, шаблон LIKE).
* **Controller (`controller.py`)** — логіка, навігація по меню, контроль 1:N, перехоплення помилок БД, заміри часу запитів.

**Дерево каталогу**

```
.
├─ app/
│  ├─ app.py               # Точка входу
│  ├─ model.py             # Модель (SQL/транзакції)
│  ├─ controller.py        # Контролер (логіка/перехоплення)
│  └─ view.py              # В'ю (консольний інтерфейс/валідації)
│
├─ requirements.txt         # Залежності (psycopg[binary], python-dotenv)
├─ .env.example             # Приклад змінних оточення (DATABASE_URL)
│
├─ LAB1_START.sql           # Створення структури БД (DDL)
├─ LAB1(DB)SH.png           # Скрін з pgAdmin (схема БД)
├─ LAB1(DB)ER.drawio.png    # ER-діаграма
│
├─ Протченко Павло КВ-34 РГР.docx   # Звіт у Word
├─ Протченко Павло КВ-34 РГР.pdf    # Звіт у PDF
│
└─ README.md 
```

---

## Схема БД та ER-діаграма

**Сутності і зв’язки:**

* `Student(student_id PK, last_name, first_name, email UQ, group_code)`
* `Instructor(instructor_id PK, last_name, first_name, email UQ, department)`
* `Course(course_id PK, title, credits, semester)`
* `Enrollment(course_id, student_id, instructor_id) PK/FK → (Course, Student, Instructor)` — **асоціативна трійка**
* `Exam(student_id, course_id, instructor_id, attempt_no) PK, FK → Enrollment` — 1:N (кілька спроб)

![ER-діаграма бази даних](./LAB1(DB)ER.drawio.png?v=2025-10-13-1)
![Скрін з pgAdmin (схема БД)](./LAB1(DB)SH.png?v=2025-10-13-1)


**DDL:**

```sql
BEGIN;

-- ===== Tables ===============================================================

CREATE TABLE IF NOT EXISTS public."Instructor"
(
    instructor_id integer NOT NULL GENERATED ALWAYS AS IDENTITY,
    last_name      varchar(60)  NOT NULL,
    first_name     varchar(60)  NOT NULL,
    email          varchar(120) NOT NULL,
    department     varchar(80)  NOT NULL,
    CONSTRAINT pk_instructor PRIMARY KEY (instructor_id),
    CONSTRAINT uq_instructor_email UNIQUE (email)
);

CREATE TABLE IF NOT EXISTS public."Student"
(
    student_id integer NOT NULL GENERATED ALWAYS AS IDENTITY,
    last_name   varchar(60)  NOT NULL,
    first_name  varchar(60)  NOT NULL,
    email       varchar(120) NOT NULL,
    group_code  varchar(20)  NOT NULL,
    CONSTRAINT pk_student PRIMARY KEY (student_id),
    CONSTRAINT uq_student_email UNIQUE (email)
);

CREATE TABLE IF NOT EXISTS public."Course"
(
    course_id integer NOT NULL GENERATED ALWAYS AS IDENTITY,
    title     varchar(120) NOT NULL,
    credits   smallint     NOT NULL,
    semester  smallint     NOT NULL,
    CONSTRAINT pk_course PRIMARY KEY (course_id),

    -- CHECK constraints
    CONSTRAINT chk_course_credits_range CHECK (credits  >= 1 AND credits  <= 10),
    CONSTRAINT chk_course_semester_range CHECK (semester >= 1 AND semester <= 12)
);

CREATE TABLE IF NOT EXISTS public."Enrollment"
(
    course_id     integer NOT NULL,
    student_id    integer NOT NULL,
    instructor_id integer NOT NULL,
    CONSTRAINT pk_enrollment PRIMARY KEY (course_id, student_id, instructor_id)
);

CREATE TABLE IF NOT EXISTS public."Exam"
(
    student_id    integer NOT NULL,
    course_id     integer NOT NULL,
    instructor_id integer NOT NULL,
    attempt_no    smallint NOT NULL,
    document      varchar(255) NOT NULL,
    exam_date     date        NOT NULL,
    grade         smallint    NOT NULL,
    CONSTRAINT pk_exam PRIMARY KEY (student_id, course_id, instructor_id, attempt_no),

    -- CHECK constraints
    CONSTRAINT chk_exam_grade_range   CHECK (grade >= 0 AND grade <= 100),
    CONSTRAINT chk_exam_attempt_nonneg CHECK (attempt_no >= 1)
);

-- ===== FKs & Cascades =======================================================

ALTER TABLE IF EXISTS public."Enrollment"
  ADD CONSTRAINT fk_enroll_student
  FOREIGN KEY (student_id)    REFERENCES public."Student"(student_id)
  ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE IF EXISTS public."Enrollment"
  ADD CONSTRAINT fk_enroll_course
  FOREIGN KEY (course_id)     REFERENCES public."Course"(course_id)
  ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE IF EXISTS public."Enrollment"
  ADD CONSTRAINT fk_enroll_instructor
  FOREIGN KEY (instructor_id) REFERENCES public."Instructor"(instructor_id)
  ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE IF EXISTS public."Exam"
  ADD CONSTRAINT fk_exam_stud_inst_cur
  FOREIGN KEY (course_id, student_id, instructor_id)
  REFERENCES public."Enrollment"(course_id, student_id, instructor_id)
  ON UPDATE CASCADE ON DELETE CASCADE;

-- ===== Performance Indexes ===============================

-- Enrollment
CREATE INDEX IF NOT EXISTS idx_enroll_course     ON public."Enrollment"(course_id);
CREATE INDEX IF NOT EXISTS idx_enroll_student    ON public."Enrollment"(student_id);
CREATE INDEX IF NOT EXISTS idx_enroll_instructor ON public."Enrollment"(instructor_id);

-- Exam
CREATE INDEX IF NOT EXISTS idx_exam_enroll ON public."Exam"(course_id, student_id, instructor_id);

END;

```

---

## Встановлення та запуск

### Вимоги

* Python **3.11–3.13**
* PostgreSQL **13+**
* `pgAdmin4`
* `psycopg[binary]` (драйвер), `python-dotenv`

### Інсталяція

```bash
git clone <https://github.com/PR0TX/Databases-and-management-tools/tree/RGR>
cd <Databases-and-management-tools>

pip install -r requirements.txt
```

### Налаштування БД та підключення

1. Створіть БД у PostgreSQL (наприклад, `kpi_exam_db`) і виконайте DDL.
2. Створіть `.env`:

```env
# .env
DATABASE_URL=postgresql://<user>:<password>@localhost:5432/kpi_exam_db
```

### Запуск застосунку

```bash
python app.py
```

При успішному підключенні отримаєте:
`[ІНФО] Підключення до БД виконано успішно.`

---

## Як користуватись (меню)

**Головне меню**

```
1) CRUD: Student
2) CRUD: Instructor
3) CRUD: Course
4) CRUD: Enrollment (трійки)
5) CRUD: Exam (спроби)
6) Генерація даних
7) Пошуки (3 запити + час виконання)
0) Вихід
```

## CRUD : перегляд перших 50 рядків; додавання/редагування/видалення.
* **Контроль 1:N**: при спробі видалити «батька» з підлеглими записами — відмова з поясненням.
* **Exam**: оновлюються лише неключові поля (`document`, `exam_date`, `grade`); `attempt_no` можна автогенерувати (наступний `MAX+1`).
---

## Генерація великих даних

### 1) `Student` — N записів (ідеально: 100 000)

```sql
INSERT INTO "Student"(last_name, first_name, email, group_code)
SELECT 
  'Last_'  || gs::text,
  'First_' || gs::text,
  'student_' || gs::text || '@example.edu',
  'KP-' || (10 + (random()*20)::int)::text
FROM generate_series(1, :N) AS gs
ON CONFLICT (email) DO NOTHING;          -- ідемпотентність
```

### 2) `Instructor` — приблизно N/100

```sql
INSERT INTO "Instructor"(last_name, first_name, email, department)
SELECT 
  'InstrL_' || gs::text,
  'InstrF_' || gs::text,
  'instructor_' || gs::text || '@univ.edu',
  'Dept_' || (1 + (random()*10)::int)::text
FROM generate_series(1, GREATEST(1, :N/100)) AS gs
ON CONFLICT (email) DO NOTHING;          -- ідемпотентність
```

### 3) `Course` — пул

```sql
INSERT INTO "Course"(title, credits, semester)
SELECT t,
       (1 + (random()*5)::int)::smallint,
       (1 + (random()*8)::int)::smallint
FROM unnest(ARRAY[
  'Databases','Algorithms','Discrete Math','Networks',
  'OS','AI','ML','SE','Web'
]) AS t
```

### 4) `Enrollment` — трійки (≈ `:N * 100`)

```sql
WITH s AS (SELECT student_id FROM "Student" ORDER BY random() LIMIT GREATEST(1, :N/2)),
     c AS (SELECT course_id  FROM "Course"  ORDER BY random() LIMIT 10),
     i AS (SELECT instructor_id FROM "Instructor" ORDER BY random() LIMIT 20)
INSERT INTO "Enrollment"(course_id, student_id, instructor_id)
SELECT c.course_id, s.student_id, i.instructor_id
FROM s CROSS JOIN c CROSS JOIN i
ON CONFLICT DO NOTHING;
```

### 5) `Exam` — 1..3 спроби на трійку (випадкові дати й оцінки)

```sql
WITH e AS (
  SELECT course_id, student_id, instructor_id
  FROM "Enrollment"
  ORDER BY random()
  LIMIT :N
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
  (now() - (random() * interval '3 years'))::date,  -- правильний 3-річний діапазон дат
  floor(random()*101)::int                           -- оцінки 0..100
FROM attempts
ON CONFLICT DO NOTHING;
```

**Рекомендований порядок масової генерації в меню:** `Student → Instructor → Course → Enrollment → Exam`.

**Примітка:** на великих `N` фактична вставка може бути меншою через `ON CONFLICT DO NOTHING`

---

## Пошукові запити та вимір часу

### Пошук 1 — Student–Exam–Course (рядки/числа/дати)

Параметри: `group_code`, `grade_min..grade_max`, `title ILIKE`, `exam_date BETWEEN`.

```sql
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
```

### Пошук 2 — Агрегація по курсу/викладачу (GROUP BY/HAVING)

Параметри: `date_from..date_to`, `min_attempts`.

```sql
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
```

### Пошук 3 — «Остання спроба» і поріг

Параметри: `semester`, `min_credits`, `fail_threshold`.

```sql
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
```

**Час виконання** виводиться контролером (Python `perf_counter`, мс) після кожного запиту.

---

## Обробка помилок та валідація

* **Валідація вводу** у `View`: `int/smallint`, дати у форматі `YYYY-MM-DD`, шаблон `LIKE` автоматично обгортається у `%...%`, якщо не містить `%/_`.

* **Перехоплення помилок БД** у `Controller.run()`:

  * `psycopg.errors.ForeignKeyViolation` 
  * `psycopg.errors.UniqueViolation` 
  * `psycopg.Error` 

* **Контроль 1:N** перед видаленням «батьків» — через методи `count_enrollments_by_*` / `count_exams_for_enrollment` у `Model`.
  Навіть якщо FK у БД має `ON DELETE CASCADE`, програма **свідомо забороняє** таке видалення, щоби **не втрачати пов'язані дані**.


---

## Контакти
* **Автор:** Протченко П.О., група **КВ-34**
* **Telegram:** [@PR0TX](https://t.me/PR0TX)
