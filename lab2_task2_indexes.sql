-- lab2_task2_indexes.sql
-- Варіант 11: GIN, HASH

-- 1. Розширення для триграмів
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- 2. GIN-індекс для ILIKE / LIKE по назві курсу
CREATE INDEX IF NOT EXISTS idx_course_title_trgm_gin
ON public."Course"
USING GIN (title gin_trgm_ops);

-- 3. Hash-індекс для рівності по групі студента
CREATE INDEX IF NOT EXISTS idx_student_group_hash
ON public."Student"
USING HASH (group_code);
