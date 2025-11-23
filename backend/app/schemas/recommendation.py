from pydantic import BaseModel
from typing import List, Optional


class RecommendedCourse(BaseModel):
    """Рекомендованный курс"""
    course_id: int
    course_name: str
    reason: str  # Причина рекомендации
    priority: int  # Приоритет (1 - высокий, 2 - средний, 3 - низкий)
    missing_skills: List[str]  # Навыки, которые восполнит курс


class RecommendationsResponse(BaseModel):
    """Ответ с рекомендациями курсов"""
    specialization_id: Optional[int] = None
    specialization_name: Optional[str] = None
    recommended_courses: List[RecommendedCourse]


class WhatIfRequest(BaseModel):
    """Запрос на моделирование смены специальности"""
    new_specialization_id: int


class WhatIfSkillComparison(BaseModel):
    """Сравнение навыка при смене специальности"""
    skill_id: int
    skill_name: str
    current_level: int
    old_required_level: int
    new_required_level: int
    will_satisfy: bool  # Хватит ли навыков для новой специальности


class WhatIfResponse(BaseModel):
    """Результат моделирования смены специальности"""
    current_specialization_id: Optional[int]
    current_specialization_name: Optional[str]
    new_specialization_id: int
    new_specialization_name: str
    current_completion_percentage: float
    new_completion_percentage: float
    skills_comparison: List[WhatIfSkillComparison]
    courses_to_keep: int  # Количество курсов, которые останутся актуальными
    total_completed_courses: int

