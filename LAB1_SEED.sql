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