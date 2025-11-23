import enum

from sqlalchemy import Column, DateTime, ForeignKey, Integer
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class CourseStatus(str, enum.Enum):
    """Статус прохождения курса"""

    ENROLLED = "enrolled"  # Записан
    IN_PROGRESS = "in_progress"  # В процессе
    COMPLETED = "completed"  # Завершен
    DROPPED = "dropped"  # Отменен


class StudentCourse(Base):
    """Прогресс студента по курсам"""

    __tablename__ = "student_courses"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)

    # Статус прохождения
    status = Column(SQLEnum(CourseStatus), default=CourseStatus.ENROLLED)

    # Уровень сложности, выбранный студентом (1 - базовый, 2 - продвинутый)
    difficulty_level = Column(Integer, default=1)

    # Оценка (если завершен)
    grade = Column(Integer, nullable=True)

    # Даты
    enrolled_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Отношения
    student = relationship("User", back_populates="student_courses")
    course = relationship("Course", back_populates="student_courses")
