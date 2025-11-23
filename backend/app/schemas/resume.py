"""Схемы для генерации резюме студента"""

from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class ResumePersonalInfo(BaseModel):
    """Личная информация для резюме"""

    name: str
    email: EmailStr
    specialization: Optional[str] = None


class ResumeSkill(BaseModel):
    """Навык в резюме с источником"""

    name: str
    level: int = Field(ge=0, le=3, description="Уровень навыка (0-3)")
    source: str = Field(description="Источник: core (основная спец) или orbit (майнер)")
    acquired_from: Optional[str] = Field(None, description="Название майнера или спецы")


class ResumeMinor(BaseModel):
    """Информация о майнере в резюме"""

    minor_name: str
    status: str = Field(description="selected, completed, archived")
    skills_gained: List[str] = Field(
        default_factory=list, description="Навыки из этого майнера"
    )


class ResumeEducation(BaseModel):
    """Образование для резюме"""

    completed_courses: int
    total_credits: int
    average_grade: Optional[float] = None


class ResumeResponse(BaseModel):
    """Полное резюме студента (основа + орбита)"""

    personal: ResumePersonalInfo

    # Все навыки (основная спец + все майнеры, включая архивные)
    skills: List[ResumeSkill]

    # Майнеры (текущие и завершённые)
    minors: List[ResumeMinor] = []

    education: ResumeEducation
    achievements: List[str]

    class Config:
        from_attributes = True
