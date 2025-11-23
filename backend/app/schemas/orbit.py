from typing import List, Optional

from pydantic import BaseModel, Field


class TargetSkill(BaseModel):
    """Целевой навык в орбите"""

    skill_id: int
    skill_name: str
    skill_description: Optional[str] = None
    required_level: int = Field(ge=0, le=3, description="Целевой уровень навыка")


class OrbitCourse(BaseModel):
    """Курс в орбите майнера"""

    course_id: int
    course_name: str
    description: Optional[str] = None
    credits: int
    semester: Optional[int] = None
    order: Optional[int] = None
    is_required: bool
    is_completed: bool = Field(description="Пройден ли студентом этот курс")
    tags: List[dict] = Field(default_factory=list, description="Теги курса с весами")


class OrbitResponse(BaseModel):
    """Орбита студента (показывает цель и структуру майнера)"""

    minor_id: int
    minor_name: str
    minor_description: Optional[str] = None
    minor_type: Optional[str] = None

    # Целевые навыки майнера (что нужно освоить)
    target_skills: List[TargetSkill] = []

    # Курсы, входящие в майнер (с отметкой о прохождении)
    courses: List[OrbitCourse] = []

    # Статистика
    total_courses: int = 0
    completed_courses: int = 0
    progress_percentage: float = Field(
        ge=0.0, le=100.0, description="Процент прохождения"
    )
