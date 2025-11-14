# ЛР‑2: Оптимізація PostgreSQL для системи обліку іспитів

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB.svg)](https://www.python.org/) [![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-336791.svg)](https://www.postgresql.org/) [![SQLAlchemy](https://img.shields.io/badge/ORM-SQLAlchemy-5C4EE5.svg)](https://www.sqlalchemy.org/)

Консольний застосунок за шаблоном MVC, який обслуговує систему **обліку екзаменаційних балів студентів**. Лабораторна робота №2 (варіант 11) сфокусована на переписуванні модуля `Model` на ORM, побудові нетривіальних індексів, створенні тригера та аналізі рівнів ізоляції PostgreSQL.

---

## Функціональність
- CRUD для сутностей `Student`, `Instructor`, `Course`, `Enrollment`, `Exam` з валідацією та контролем 1:N на рівні контролера й тригера.
- Генерація великих тестових наборів (до 100k студентів) та пакетні сценарії створення пов’язаних сутностей.
- Три пошукові запити з параметрами, JOIN/віконними функціями й виміром часу виконання.
- SQL-артефакти для порівняння планів запитів, тестування тригера та репродукції ізоляційних сценаріїв.

---

## Стек і вимоги
- Python 3.11–3.13, SQLAlchemy 2.x, psycopg3, python-dotenv.
- PostgreSQL 13+ із розширенням `pg_trgm` (для GIN).
- ОС Linux/macOS/Windows; pgAdmin 4 використовувався для планів запитів.

---

## Швидкий старт
```bash
git clone https://github.com/PR0TX/Databases-and-management-tools.git
cd "Databases and management tools/Laboratory/2"
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Створіть `.env`  і виконайте `LAB2_START.sql`:
```env
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/kpi_exam_db
```

Запуск консольного клієнта:
```bash
python app/app.py
```

---

## Завдання ЛР‑2

### 1. ORM (app/model.py, app/orm_models.py)
- Увесь доступ до БД переведено з сирих SQL на SQLAlchemy ORM (future‑style Engine + Session). Сигнатури методів моделі залишилися сумісними з існуючим `controller.py`/`view.py`.
- Впроваджено контекстний менеджер `_session()` з єдиною точкою коміта/rollback та перехопленням `IntegrityError`.
- CRUD, генератори даних та складні пошуки тепер описані декларативно; асоціативна трійка `Enrollment` і PK `Exam` представлені комбінованими ключами та відношеннями `relationship()`.

### 2. Індекси та вимір ефекту (lab2_task2_indexes.sql, tests/2/*.txt)
- Варіант вимагає **GIN** (триграмний, `idx_course_title_trgm_gin`) та **HASH** індекси (`idx_student_group_hash`). Розширення `pg_trgm` підключається скриптом.
- Набір тестових запитів (`tests/2/1.txt` … `5.txt`) і EXPLAIN ANALYZE дозволяють порівняти продуктивність до/після індексації. Спостережувані результати:  
  - Пошук 1 (Student–Exam–Course із фільтром по групі та назві курсу): 54.96 → 54.37 мс за рахунок Bitmap Heap Scan на HASH‑індексі.  
  - Пошук 2 (агрегація по курсу/викладачу): 82.04 → 74.88 мс (~9% виграш).  
  - Пошук 3 (статистика по групі): 46.99 → 37.63 мс (~20% виграш).  
  - Фільтри за `Course.title` та `Student.group_code` більше не покладаються тільки на послідовне читання.  

### 3. Тригер BEFORE UPDATE/DELETE (lab2_task3_indexes.sql, tests/3/*.txt)
- `public.fn_instructor_before_ud` перевіряє залежні рядки `Enrollment/Exam` перед видаленням викладача, і блокує операцію з кодом `23503`, якщо вони існують (курсори + COUNT).  
- Під час оновлення валідується email (наявність `@`) та протоколюється зміна кафедри/пошти через `RAISE NOTICE` з безпечним exception‑handling.  

### 4. Рівні ізоляції транзакцій (tests/text.txt, розділ 2.6)
- Сценарії READ COMMITTED (нестабільні читання, фантоми), REPEATABLE READ та SERIALIZABLE (write skew) на реальних даних.  
- Кожний кейс описує послідовність кроків у двох сесіях, SQL-команди та очікувані повідомлення PostgreSQL, що можна повторити в psql/pgAdmin.

---

## ER-діаграма та схема БД
- Логічні зв’язки та атрибути відображено на ER-діаграмі, яка використовувалась у ЛР‑1 та актуальна для цієї роботи:

  ![ER-діаграма БД](<./LAB1(DB)ER.png>)

- Схема з pgAdmin показує реальну структуру таблиць і FK, що застосовується при запуску застосунку:

  ![Схема в pgAdmin](<./LAB1(DB)SH.png>)

---

## Меню застосунку
```
1) CRUD: Student        5) CRUD: Exam (спроби)
2) CRUD: Instructor     6) Генерація даних (масові вставки)
3) CRUD: Course         7) Пошук із виміром часу (3 сценарії)
4) CRUD: Enrollment     0) Вихід
```
- CRUD‑операції відображають перші 50 рядків, автогенерують `attempt_no`, перевіряють FK перед створенням.  
- Масова генерація (пункти 6.1–6.6) відтворює пайплайн Student→Instructor→Course→Enrollment→Exam.  
- Пошуки використовують ORM‑вирази, window‑функції й повертають час виконання в мілісекундах.

---

## Структура репозиторію
```
app/
 ├─ app.py            # точка входу, завантаження .env
 ├─ controller.py     # бізнес-логіка, меню, вимір часу
 ├─ model.py          # ORM-операції та генератори
 ├─ orm_models.py     # декларативні сутності
 └─ view.py           # консольний інтерфейс/валідація
lab2_task2_indexes.sql   # GIN/HASH індекси (завдання 2)
lab2_task3_indexes.sql   # тригер BEFORE UPDATE/DELETE (завдання 3)
LAB2_START.sql           # база для запуску бази
tests/
 ├─ 2/*.txt             # EXPLAIN ANALYZE для індексів
 └─ 3/*.txt             # сценарії перевірки тригера
```

---

## Контакти
- Протченко Павло (КВ‑34)  
- Telegram: [@PR0TX](https://t.me/PR0TX)
