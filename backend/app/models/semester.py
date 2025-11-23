from sqlalchemy import Column, Integer, String, Date
from app.database import Base


class Semester(Base):
    """Модель семестра"""
    __tablename__ = "semesters"

    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, nullable=False)  # Учебный год (например, 2024)
    number = Column(Integer, nullable=False)  # Номер семестра (1 - осенний, 2 - весенний)
    name = Column(String, nullable=True)  # Название (например, "Осень 2024")
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)

