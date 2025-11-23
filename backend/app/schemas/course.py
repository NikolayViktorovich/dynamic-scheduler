from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from app.models.student_course import CourseStatus


class CourseBase(BaseModel):
    """Базовая схема курса"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    credits: int = Field(default=3, ge=1, le=10)
    semester: Optional[int] = Field(None, ge=1, le=12)
    is_elective: bool = False


class CourseCreate(CourseBase):
    """Схема для создания курса"""
    specialization_id: Optional[int] = None
    difficulty_levels: Optional[Dict[str, int]] = None


class CourseUpdate(BaseModel):
    """Схема для обновления курса"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    credits: Optional[int] = Field(None, ge=1, le=10)
    semester: Optional[int] = Field(None, ge=1, le=12)
    is_elective: Optional[bool] = None
    specialization_id: Optional[int] = None


class SkillInCourse(BaseModel):
    """Навык в курсе"""
    skill_id: int
    skill_name: str
    difficulty_level: int
    skill_weight: int


class CourseResponse(CourseBase):
    """Схема ответа с курсом"""
    id: int
    specialization_id: Optional[int] = None
    difficulty_levels: Optional[Dict[str, int]] = None
    
    class Config:
        from_attributes = True


class CourseDetailResponse(CourseResponse):
    """Детальная информация о курсе"""
    skills: List[SkillInCourse] = []


class CourseEnrollRequest(BaseModel):
    """Запрос на запись на курс"""
    difficulty_level: int = Field(default=1, ge=1, le=2)


class CourseCompleteRequest(BaseModel):
    """Запрос на завершение курса"""
    grade: int = Field(..., ge=0, le=100)


class StudentCourseResponse(BaseModel):
    """Информация о курсе студента"""
    id: int
    course_id: int
    course_name: str
    status: CourseStatus
    difficulty_level: int
    grade: Optional[int] = None
    enrolled_at: datetime
    completed_at: Optional[datetime] = None
    credits: int
    
    class Config:
        from_attributes = True

