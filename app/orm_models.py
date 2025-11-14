# orm_models.py
from __future__ import annotations
from typing import List
from sqlalchemy import (
    String, Integer, SmallInteger, Date, CheckConstraint, UniqueConstraint,
    ForeignKeyConstraint, PrimaryKeyConstraint
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass


# --- Student ---------------------------------------------------------------
class Student(Base):
    __tablename__ = 'Student'
    __table_args__ = (
        UniqueConstraint('email', name='uq_student_email'),
        {'schema': 'public'},
    )

    student_id: Mapped[int]       = mapped_column(Integer, primary_key=True, autoincrement=True)
    last_name:  Mapped[str]       = mapped_column(String(60), nullable=False)
    first_name: Mapped[str]       = mapped_column(String(60), nullable=False)
    email:      Mapped[str]       = mapped_column(String(120), nullable=False)
    group_code: Mapped[str]       = mapped_column(String(20), nullable=False)

    enrollments: Mapped[List["Enrollment"]] = relationship(back_populates="student")


# --- Instructor ------------------------------------------------------------
class Instructor(Base):
    __tablename__ = 'Instructor'
    __table_args__ = (
        UniqueConstraint('email', name='uq_instructor_email'),
        {'schema': 'public'},
    )

    instructor_id: Mapped[int]    = mapped_column(Integer, primary_key=True, autoincrement=True)
    last_name:     Mapped[str]    = mapped_column(String(60), nullable=False)
    first_name:    Mapped[str]    = mapped_column(String(60), nullable=False)
    email:         Mapped[str]    = mapped_column(String(120), nullable=False)
    department:    Mapped[str]    = mapped_column(String(80), nullable=False)

    enrollments: Mapped[List["Enrollment"]] = relationship(back_populates="instructor")


# --- Course ---------------------------------------------------------------
class Course(Base):
    __tablename__ = 'Course'
    __table_args__ = (
        CheckConstraint('credits  >= 1 AND credits  <= 10', name='chk_course_credits_range'),
        CheckConstraint('semester >= 1 AND semester <= 12', name='chk_course_semester_range'),
        {'schema': 'public'},
    )

    course_id: Mapped[int]        = mapped_column(Integer, primary_key=True, autoincrement=True)
    title:     Mapped[str]        = mapped_column(String(120), nullable=False)
    credits:   Mapped[int]        = mapped_column(SmallInteger, nullable=False)
    semester:  Mapped[int]        = mapped_column(SmallInteger, nullable=False)

    enrollments: Mapped[List["Enrollment"]] = relationship(back_populates="course")


# --- Enrollment (PK: course_id, student_id, instructor_id) ----------------
class Enrollment(Base):
    __tablename__ = 'Enrollment'


    __table_args__ = (
        PrimaryKeyConstraint('course_id', 'student_id', 'instructor_id', name='pk_enrollment'),
        ForeignKeyConstraint(
            ['course_id'],
            ['public."Course".course_id'],
            onupdate="CASCADE", ondelete="CASCADE"
        ),
        ForeignKeyConstraint(
            ['student_id'],
            ['public."Student".student_id'],
            onupdate="CASCADE", ondelete="CASCADE"
        ),
        ForeignKeyConstraint(
            ['instructor_id'],
            ['public."Instructor".instructor_id'],
            onupdate="CASCADE", ondelete="CASCADE"
        ),
        {'schema': 'public'},
    )

    # зв’язки
    course:     Mapped["Course"]     = relationship(back_populates="enrollments")
    student:    Mapped["Student"]    = relationship(back_populates="enrollments")
    instructor: Mapped["Instructor"] = relationship(back_populates="enrollments")


# --- Exam (PK: student_id, course_id, instructor_id, attempt_no) ----------
class Exam(Base):
    __tablename__ = 'Exam'
    __table_args__ = (
        PrimaryKeyConstraint('student_id', 'course_id', 'instructor_id', 'attempt_no', name='pk_exam'),
        CheckConstraint('grade >= 0 AND grade <= 100', name='chk_exam_grade_range'),
        CheckConstraint('attempt_no >= 1',                name='chk_exam_attempt_nonneg'),
        ForeignKeyConstraint(
            ['course_id', 'student_id', 'instructor_id'],
            ['public."Enrollment".course_id', 'public."Enrollment".student_id', 'public."Enrollment".instructor_id'],
            onupdate="CASCADE", ondelete="CASCADE"
        ),
        {'schema': 'public'},
    )

    student_id:    Mapped[int]        = mapped_column(Integer, nullable=False)
    course_id:     Mapped[int]        = mapped_column(Integer, nullable=False)
    instructor_id: Mapped[int]        = mapped_column(Integer, nullable=False)
    attempt_no:    Mapped[int]        = mapped_column(SmallInteger, nullable=False)
    document:      Mapped[str]        = mapped_column(String(255), nullable=False)
    exam_date:     Mapped["Date"]     = mapped_column(Date, nullable=False)
    grade:         Mapped[int]        = mapped_column(SmallInteger, nullable=False)
