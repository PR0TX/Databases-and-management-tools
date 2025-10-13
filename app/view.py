# view.py
# Консольний UI: показ меню, читання вводу, вивід таблиць/помилок.
# Валідація базових типів (int, smallint, date, email/рядок).

from datetime import date

class View:
    # ----------- Основні меню -----------
    def main_menu(self) -> str:
        print("\n=== Головне меню ===")
        print("1) CRUD: Student")
        print("2) CRUD: Instructor")
        print("3) CRUD: Course")
        print("4) CRUD: Enrollment (трійки)")
        print("5) CRUD: Exam (спроби)")
        print("6) Генерація даних")
        print("7) Пошуки (3 запити + час виконання)")
        print("0) Вихід")
        return input("> ").strip()

    def submenu_crud(self, title:str) -> str:
        print(f"\n--- {title} ---")
        print("1) Перегляд (перші 50)")
        print("2) Додати")
        print("3) Оновити")
        print("4) Видалити")
        print("0) Назад")
        return input("> ").strip()

    def submenu_generate(self) -> str:
        print("\n--- Генерація ---")
        print("1) Student (N)")
        print("2) Instructor (~N/100)")
        print("3) Course (пул курсів)")
        print("4) Enrollment (із наявних)")
        print("5) Exam (із наявних)")
        print("6) Масова генерація (рекомендований порядок 1→2→3→4→5)")
        print("0) Назад")
        return input("> ").strip()

    def submenu_searches(self) -> str:
        print("\n--- Пошуки ---")
        print("1) За групою + діапазон оцінок + шаблон курсу + діапазон дат")
        print("2) Середній бал/кількість спроб по курсах і викладачах за датами")
        print("3) Хто провалив при заданому семестрі/кредитах (мін. бал нижче порогу)")
        print("0) Назад")
        return input("> ").strip()

    # ----------- Ввід/вивід/валідація -----------
    def show_rows(self, rows:list[dict]):
        if not rows:
            print("(порожньо)")
            return
        for r in rows:
            print(r)

    def info(self, msg:str):
        print(f"[ІНФО] {msg}")

    def warn(self, msg:str):
        print(f"[УВАГА] {msg}")

    def err(self, msg:str):
        print(f"[ПОМИЛКА] {msg}")

    def ask_str(self, prompt:str, allow_empty=False) -> str:
        while True:
            s = input(prompt).strip()
            if s or allow_empty:
                return s
            print("Поле не може бути порожнім.")

    def ask_int(self, prompt:str, min_val:int|None=None, max_val:int|None=None) -> int:
        while True:
            s = input(prompt).strip()
            try:
                v = int(s)
                if (min_val is None or v >= min_val) and (max_val is None or v <= max_val):
                    return v
            except ValueError:
                pass
            print("Введіть коректне ціле число" + (f" (від {min_val})" if min_val is not None else "") +
                  (f" (до {max_val})" if max_val is not None else "") + ".")

    def ask_smallint(self, prompt:str, min_val:int|None=None, max_val:int|None=None) -> int:
        return self.ask_int(prompt, min_val if min_val is not None else -32768,
                            max_val if max_val is not None else 32767)

    def ask_date_iso(self, prompt:str) -> str:
        while True:
            s = input(prompt).strip()
            try:
                y, m, d = s.split("-")
                _ = date(int(y), int(m), int(d))
                return s
            except Exception:
                print("Дата має бути у форматі YYYY-MM-DD.")

    def ask_like_pattern(self, prompt:str) -> str:
        s = input(prompt).strip()
        if "%" not in s and "_" not in s:
            return f"%{s}%"
        return s

    def confirm(self, prompt:str) -> bool:
        s = input(f"{prompt} [y/N]: ").strip().lower()
        return s in ("y", "yes", "д", "так")
