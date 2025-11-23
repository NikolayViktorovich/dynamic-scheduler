from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import date


class SpecializationBase(BaseModel):
    """Базовая схема специальности"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    market_demand: float = Field(default=0.0, ge=0, le=100)
    duration_years: int = Field(default=2, ge=1, le=6)


class SpecializationCreate(SpecializationBase):
    """Схема для создания специальности"""
    required_skills: Optional[Dict[int, int]] = None


class SpecializationUpdate(BaseModel):
    """Схема для обновления специальности"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    market_demand: Optional[float] = Field(None, ge=0, le=100)
    duration_years: Optional[int] = Field(None, ge=1, le=6)
    required_skills: Optional[Dict[int, int]] = None


class SpecializationResponse(SpecializationBase):
    """Схема ответа со специальностью"""
    id: int
    required_skills: Optional[Dict[int, int]] = None
    
    class Config:
        from_attributes = True


class CourseInRoadmap(BaseModel):
    """Курс в roadmap"""
    id: int
    name: str
    semester: int
    is_elective: bool
    credits: int


class RoadmapResponse(BaseModel):
    """Roadmap образовательной траектории"""
    specialization_id: int
    specialization_name: str
    duration_years: int
    semesters: Dict[int, List[CourseInRoadmap]]  # {semester_number: [courses]}
    total_credits: int


class SkillRequirement(BaseModel):
    """Требуемый навык"""
    skill_id: int
    skill_name: str
    required_level: int
    current_level: Optional[int] = 0


class SkillsMatrixResponse(BaseModel):
    """Матрица навыков специальности"""
    specialization_id: int
    specialization_name: str
    required_skills: List[SkillRequirement]

