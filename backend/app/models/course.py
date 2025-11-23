from sqlalchemy import JSON, Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Course(Base):
    """Модель курса"""

    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    credits = Column(Integer, default=3)  # Зачетные единицы
    semester = Column(Integer, nullable=True)  # Рекомендуемый семестр
    is_elective = Column(Boolean, default=False)  # Элективный или обязательный

    # Связь со специальностью
    specialization_id = Column(Integer, ForeignKey("specializations.id"), nullable=True)

    # JSON структура уровней сложности: {"base": 1, "advanced": 2}
    difficulty_levels = Column(JSON, nullable=True)

    # Отношения
    specialization = relationship("Specialization", back_populates="courses")
    course_skills = relationship(
        "CourseSkill", back_populates="course", cascade="all, delete-orphan"
    )
    student_courses = relationship(
        "StudentCourse", back_populates="course", cascade="all, delete-orphan"
    )
    prerequisites = relationship(
        "CourseDependency",
        foreign_keys="CourseDependency.course_id",
        back_populates="course",
        cascade="all, delete-orphan",
    )
    tags = relationship(
        "CourseTag", back_populates="course", cascade="all, delete-orphan"
    )
    minor_courses = relationship(
        "MinorCourse", back_populates="course", cascade="all, delete-orphan"
    )


class CourseDependency(Base):
    """Модель зависимостей (пререквизитов) между курсами"""

    __tablename__ = "course_dependencies"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    prerequisite_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    is_hard_dependency = Column(Boolean, default=True)  # Жесткое или мягкое требование

    # Отношения
    course = relationship(
        "Course", foreign_keys=[course_id], back_populates="prerequisites"
    )
    prerequisite = relationship("Course", foreign_keys=[prerequisite_id])
