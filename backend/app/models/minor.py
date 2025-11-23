from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Minor(Base):
    """Модель майнера (дополнительного образования)"""

    __tablename__ = "minors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    # Тип майнера: углубление, смена области, soft-skills и т.п.
    minor_type = Column(String, nullable=True)

    # Признак активности
    is_active = Column(Boolean, default=True)

    # Отношения
    minor_skills = relationship(
        "MinorSkill", back_populates="minor", cascade="all, delete-orphan"
    )
    minor_courses = relationship(
        "MinorCourse", back_populates="minor", cascade="all, delete-orphan"
    )
    user_minors = relationship(
        "UserMinor", back_populates="minor", cascade="all, delete-orphan"
    )


class MinorSkill(Base):
    """Целевые навыки майнера (что должен уметь выпускник этого майнера)"""

    __tablename__ = "minor_skills"

    id = Column(Integer, primary_key=True, index=True)
    minor_id = Column(Integer, ForeignKey("minors.id"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)

    # Целевой уровень навыка для этого майнера (0-3)
    required_level = Column(Integer, default=1, nullable=False)

    # Отношения
    minor = relationship("Minor", back_populates="minor_skills")
    skill = relationship("Skill")


class MinorCourse(Base):
    """Курсы, входящие в майнер (многие ко многим)"""

    __tablename__ = "minor_courses"

    id = Column(Integer, primary_key=True, index=True)
    minor_id = Column(Integer, ForeignKey("minors.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)

    # Опциональный порядок курса в майнере (для рекомендации последовательности)
    order = Column(Integer, nullable=True)

    # Обязательный или элективный в рамках майнера
    is_required = Column(Boolean, default=True)

    # Отношения
    minor = relationship("Minor", back_populates="minor_courses")
    course = relationship("Course", back_populates="minor_courses")


class UserMinor(Base):
    """Выбранные майнеры студента"""

    __tablename__ = "user_minors"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    minor_id = Column(Integer, ForeignKey("minors.id"), nullable=False)

    # Статус: selected (текущий), completed (завершённый), archived (отменён/заменён)
    status = Column(String, default="selected", nullable=False)

    # Отношения
    user = relationship("User", back_populates="user_minors")
    minor = relationship("Minor", back_populates="user_minors")
