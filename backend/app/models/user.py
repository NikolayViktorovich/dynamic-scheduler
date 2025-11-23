from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class User(Base):
    """Модель пользователя (студента)"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # ID выбранной специальности (может быть null, если не выбрана)
    specialization_id = Column(Integer, nullable=True)

    # Отношения
    student_courses = relationship(
        "StudentCourse", back_populates="student", cascade="all, delete-orphan"
    )
    student_skills = relationship(
        "StudentSkill", back_populates="student", cascade="all, delete-orphan"
    )
    user_minors = relationship(
        "UserMinor", back_populates="user", cascade="all, delete-orphan"
    )

    @property
    def minor_ids(self) -> list[int]:
        return [m.minor_id for m in self.user_minors]
