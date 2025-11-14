-- ============================================================
-- ЛР2, завдання 3. Варіант 11: BEFORE UPDATE, DELETE
-- Тригер на public."Instructor"
-- ============================================================

-- 1) Видаляємо тригер, якщо він вже існує
DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM pg_trigger
        WHERE tgname = 'trg_instructor_before_update_delete'
          AND tgrelid = 'public."Instructor"'::regclass
    ) THEN
        EXECUTE 'DROP TRIGGER trg_instructor_before_update_delete ON public."Instructor"';
    END IF;
END;
$$;

-- 2) Створюємо / перезатираємо функцію-тригер
CREATE OR REPLACE FUNCTION public.fn_instructor_before_ud()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    -- курсор по всіх Enrollment для цього викладача
    enr_cur CURSOR FOR
        SELECT e.course_id, e.student_id, e.instructor_id
        FROM public."Enrollment" e
        WHERE e.instructor_id = OLD.instructor_id;

    enr_row    RECORD;
    enr_count  integer := 0;
    exam_count integer := 0;
BEGIN
    -- =========================
    -- Гілка для BEFORE DELETE
    -- =========================
    IF TG_OP = 'DELETE' THEN

        -- Курсорний цикл по Enrollment
        OPEN enr_cur;
        LOOP
            FETCH enr_cur INTO enr_row;
            EXIT WHEN NOT FOUND;
            enr_count := enr_count + 1;
        END LOOP;
        CLOSE enr_cur;


        SELECT COUNT(*) INTO exam_count
        FROM public."Exam" ex
        WHERE ex.instructor_id = OLD.instructor_id;

        -- Якщо є хоча б один залежний запис — забороняємо видалення
        IF enr_count > 0 OR exam_count > 0 THEN
            RAISE EXCEPTION
                'Видалення викладача % заборонено: знайдено % рядків в Enrollment і % в Exam.',
                OLD.instructor_id, enr_count, exam_count
                USING ERRCODE = '23503';  -- foreign_key_violation
        ELSE
            RAISE NOTICE
                'Видалення викладача % дозволено: залежних рядків не знайдено.',
                OLD.instructor_id;
        END IF;

        RETURN OLD;  -- для BEFORE DELETE повертаємо OLD

    -- =========================
    -- Гілка для BEFORE UPDATE
    -- =========================
    ELSIF TG_OP = 'UPDATE' THEN
        BEGIN
            -- Якщо змінюється email
            IF NEW.email IS DISTINCT FROM OLD.email THEN
                IF position('@' IN NEW.email) = 0 THEN
                    RAISE EXCEPTION
                        'Невірний email "%". Поле email має містити "@".',
                        NEW.email
                        USING ERRCODE = '22000';  -- data exception
                END IF;

                RAISE NOTICE
                    'Викладачу % змінено email з % на %',
                    NEW.instructor_id, OLD.email, NEW.email;
            END IF;

            -- Якщо змінюється кафедра
            IF NEW.department IS DISTINCT FROM OLD.department THEN
                RAISE NOTICE
                    'Викладачу % змінено кафедру з % на %',
                    NEW.instructor_id, OLD.department, NEW.department;
            END IF;

        EXCEPTION
            WHEN others THEN
                RAISE EXCEPTION
                    'Помилка в тригері fn_instructor_before_ud() при оновленні викладача %: %',
                    COALESCE(NEW.instructor_id, OLD.instructor_id), SQLERRM;
        END;

        RETURN NEW;  -- для BEFORE UPDATE повертаємо NEW
    END IF;

    RETURN NEW;
END;
$$;

-- 3) Створюємо тригер
CREATE TRIGGER trg_instructor_before_update_delete
BEFORE UPDATE OR DELETE
ON public."Instructor"
FOR EACH ROW
EXECUTE FUNCTION public.fn_instructor_before_ud();
