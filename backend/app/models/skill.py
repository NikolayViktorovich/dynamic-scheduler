from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Skill(Base):
    """Модель навыка (древовидная структура)"""
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # Древовидная структура (self-referencing)
    parent_id = Column(Integer, ForeignKey("skills.id"), nullable=True)
    
    # Уровень в иерархии (0 - корень, 1 - первый уровень, и т.д.)
    level = Column(Integer, default=0)
    
    # Отношения
    parent = relationship("Skill", remote_side=[id], backref="children")
    course_skills = relationship("CourseSkill", back_populates="skill", cascade="all, delete-orphan")
    student_skills = relationship("StudentSkill", back_populates="skill", cascade="all, delete-orphan")


class CourseSkill(Base):
    """Связь курса и навыков, которые он дает"""
    __tablename__ = "course_skills"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    
    # Уровень сложности курса (1 - базовый, 2 - продвинутый)
    difficulty_level = Column(Integer, default=1)
    
    # Вес навыка (сколько "единиц" навыка дает курс на данном уровне)
    skill_weight = Column(Integer, default=1)
    
    # Отношения
    course = relationship("Course", back_populates="course_skills")
    skill = relationship("Skill", back_populates="course_skills")


class StudentSkill(Base):
    """Текущие навыки студента"""
    __tablename__ = "student_skills"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    
    # Уровень владения навыком (суммарный вес со всех курсов)
    level = Column(Integer, default=0)
    
    # Источник получения навыка (для трекинга)
    acquired_from = Column(String, nullable=True)
    
    # Отношения
    student = relationship("User", back_populates="student_skills")
    skill = relationship("Skill", back_populates="student_skills")

