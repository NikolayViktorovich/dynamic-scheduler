from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class CourseTag(Base):
    """Теги курсов с весами (дифференцированные)"""

    __tablename__ = "course_tags"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    tag_name = Column(String, nullable=False, index=True)

    # Вес тега (1.0 - 3.0): насколько важен/централен этот тег для курса
    # Например: python=3.0, fastapi=1.0, backend=2.0
    weight = Column(Float, default=1.0, nullable=False)

    # Отношения
    course = relationship("Course", back_populates="tags")
