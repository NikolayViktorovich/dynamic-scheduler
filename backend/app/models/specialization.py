from sqlalchemy import Column, Integer, String, Text, Float, JSON
from sqlalchemy.orm import relationship
from app.database import Base


class Specialization(Base):
    """Модель специальности"""
    __tablename__ = "specializations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text, nullable=True)
    market_demand = Column(Float, default=0.0)  # Оценка востребованности на рынке (0-100)
    duration_years = Column(Integer, default=2)  # Длительность обучения в годах
    
    # JSON структура требуемых навыков: {skill_id: required_level}
    required_skills = Column(JSON, nullable=True)
    
    # Отношения
    courses = relationship("Course", back_populates="specialization")

