# Лабораторна робота №1 · Система обліку екзаменаційних балів студентів

## 🔎 Огляд
Система зберігає довідники студентів, викладачів і курсів, фіксує **призначення трійок** *Student–Course–Instructor* та **історію спроб складання іспитів** з балами і датами. Окрема таблиця `Exam` дозволяє вести повну історію перескладань і будувати звіти (остання/найкраща оцінка тощо).

---

## 🗂 Схема БД (таблиці)

**Student**
- `student_id` (PK, identity)
- `last_name`, `first_name`
- `email` (UNIQUE)
- `group_code`

**Instructor**
- `instructor_id` (PK, identity)
- `last_name`, `first_name`
- `email` (UNIQUE)
- `department`

**Course**
- `course_id` (PK, identity)
- `title`
- `credits` *(CHECK: валідний діапазон)*
- `semester` *(CHECK: валідний діапазон)*

**Enrollment** — асоціативна сутність 3-мірного зв’язку
- PK: ⟨`course_id`, `student_id`, `instructor_id`⟩
- FK: `course_id` → `Course`, `student_id` → `Student`, `instructor_id` → `Instructor`
- `ON UPDATE/DELETE CASCADE`

**Exam** — подієва сутність «спроба іспиту»
- PK: ⟨`student_id`, `course_id`, `instructor_id`, `attempt_no`⟩
- FK: ⟨`course_id`, `student_id`, `instructor_id`⟩ → `Enrollment` (CASCADE)
- Атрибути: `attempt_no` *(CHECK: ≥ 1)*, `document`, `exam_date` *(NOT NULL)*, `grade` *(CHECK: 0..100)*

> **Нормалізація**: усі таблиці відповідають 1НФ–3НФ; у `Enrollment` немає неключових атрибутів; у `Exam` всі атрибути залежать від усього складеного ключа.

---

## 🧭 Архітектурні рішення
- **Трійка `Enrollment`**: фіксує факт «студент навчається на курсі у конкретного викладача»; це опора для подій (іспити).
- **Окрема `Exam`**: вся історія спроб (№, дата, бал, документ); легко отримати останню/найкращу оцінку без дублювання в `Enrollment`.
- **Цілісність**: каскадні дії на FK; унікальність e-mail; `CHECK`-обмеження.
- **Продуктивність**: окремі індекси на FK (PostgreSQL не індексує їх автоматично).

---

## 🔧 Розгортання

### Вимоги

* **PostgreSQL 16+**
* **pgAdmin 4** або `psql`

### Кроки

1. Створити БД .
2. Виконати DDL-скрипт (створює таблиці, ключі, обмеження):

   ```bash
   psql -d exams_db -f LAB1_START.sql
   ```
3. (Опційно) Завантажити тестові дані:

   ```bash
   psql -d exams_db -f LAB1_SEED.sql
   ```

---

## 🧪 Мінімальні тестові дані

```sql
-- Instructors
INSERT INTO "Instructor"(last_name, first_name, email, department) VALUES
('Коваленко','Олена','o.kovalenko@uni.edu','ІТ'),
('Іванов','Петро','p.ivanov@uni.edu','Математика'),
('Савчук','Дарія','d.savchuk@uni.edu','Фізика');

-- Students
INSERT INTO "Student"(last_name, first_name, email, group_code) VALUES
('Сидоренко','Марія','m.sydorenko@uni.edu','КВ-21'),
('Бондар','Андрій','a.bondar@uni.edu','КВ-22'),
('Ченко','Ілля','i.chenko@uni.edu','КВ-23');

-- Courses
INSERT INTO "Course"(title, credits, semester) VALUES
('Бази даних',5,3), ('Алгоритми',6,3), ('Вища математика',4,1);

-- Enrollments (course_id, student_id, instructor_id)
INSERT INTO "Enrollment" VALUES (1,1,1),(2,2,2),(3,3,3);

-- Exam attempts
INSERT INTO "Exam" VALUES
(1,1,1,1,'doc_1','2025-01-20',58),
(1,1,1,2,'doc_2','2025-02-10',82),
(2,2,2,1,'doc_3','2025-01-22',74),
(3,3,3,1,'doc_4','2025-01-18',91);
```

---

## 🖼 ER-діаграма

![ER-діаграма бази даних](./LAB1(DB).drawio.png)

---

## 👤 Автор

**Протченко Павло, КВ-34**
Telegram: [@PR0TX](https://t.me/PR0TX)

```
```
