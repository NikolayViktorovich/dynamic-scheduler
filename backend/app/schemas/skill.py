from typing import List, Optional

from pydantic import BaseModel, Field


class SkillBase(BaseModel):
    """Базовая схема навыка"""

    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    parent_id: Optional[int] = None
    level: int = Field(default=0, ge=0)


class SkillCreate(SkillBase):
    """Схема для создания навыка"""

    pass


class SkillResponse(SkillBase):
    """Схема ответа с навыком"""

    id: int

    class Config:
        from_attributes = True


class SkillTreeNode(BaseModel):
    """Узел дерева навыков"""

    id: int
    name: str
    description: Optional[str] = None
    level: int
    parent_id: Optional[int] = None
    children: List["SkillTreeNode"] = []

    class Config:
        from_attributes = True


class StudentSkillResponse(BaseModel):
    """Навык студента"""

    skill_id: int
    skill_name: str
    level: int
    acquired_from: Optional[str] = None


class GapAnalysisItem(BaseModel):
    """Элемент анализа дефицита навыков"""

    skill_id: int
    skill_name: str
    required_level: int
    current_level: int
    gap: int  # Дефицит (положительное число = не хватает)
    is_satisfied: bool  # Достаточно ли навыков


class GapAnalysisResponse(BaseModel):
    """Результат анализа дефицита навыков"""

    specialization_id: int
    specialization_name: str
    total_required_skills: int
    satisfied_skills: int
    completion_percentage: float
    gaps: List[GapAnalysisItem]
