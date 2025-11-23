from typing import List, Optional

from pydantic import BaseModel, Field

# ============= Теги курсов =============


class CourseTagBase(BaseModel):
    """Базовая схема тега курса"""

    tag_name: str
    weight: float = Field(default=1.0, ge=0.0, le=3.0, description="Вес тега (0-3)")


class CourseTagCreate(CourseTagBase):
    """Схема для создания тега курса"""

    course_id: int


class CourseTag(CourseTagBase):
    """Полная схема тега курса"""

    id: int
    course_id: int

    class Config:
        from_attributes = True


class CourseTagSimple(BaseModel):
    """Простая схема тега для отображения (без id и course_id)"""

    tag_name: str
    weight: float

    class Config:
        from_attributes = True


# ============= Майнеры =============


class MinorBase(BaseModel):
    """Базовая схема майнера"""

    name: str
    description: Optional[str] = None
    minor_type: Optional[str] = None


class MinorCreate(MinorBase):
    """Схема для создания майнера"""

    pass


class MinorUpdate(BaseModel):
    """Схема для обновления майнера"""

    name: Optional[str] = None
    description: Optional[str] = None
    minor_type: Optional[str] = None
    is_active: Optional[bool] = None


class Minor(MinorBase):
    """Полная схема майнера"""

    id: int
    is_active: bool

    class Config:
        from_attributes = True


# ============= Навыки майнера =============


class MinorSkillBase(BaseModel):
    """Базовая схема навыка майнера"""

    skill_id: int
    required_level: int = Field(ge=0, le=3, description="Требуемый уровень (0-3)")


class MinorSkillCreate(MinorSkillBase):
    """Схема для создания навыка майнера"""

    minor_id: int


class MinorSkill(MinorSkillBase):
    """Полная схема навыка майнера"""

    id: int
    minor_id: int

    class Config:
        from_attributes = True


# ============= Курсы майнера =============


class MinorCourseBase(BaseModel):
    """Базовая схема курса в майнере"""

    course_id: int
    order: Optional[int] = None
    is_required: bool = True


class MinorCourseCreate(MinorCourseBase):
    """Схема для создания курса в майнере"""

    minor_id: int


class MinorCourse(MinorCourseBase):
    """Полная схема курса в майнере"""

    id: int
    minor_id: int

    class Config:
        from_attributes = True


# ============= Выбор майнера студентом =============


class UserMinorBase(BaseModel):
    """Базовая схема выбора майнера"""

    minor_id: int


class UserMinorCreate(UserMinorBase):
    """Схема для выбора майнера"""

    pass


class UserMinorUpdate(BaseModel):
    """Схема для обновления статуса майнера"""

    status: str = Field(description="selected, completed, archived")


class UserMinor(UserMinorBase):
    """Полная схема выбора майнера"""

    id: int
    user_id: int
    status: str

    class Config:
        from_attributes = True


# ============= Детальные схемы с вложенными данными =============


class SkillInfo(BaseModel):
    """Информация о навыке"""

    id: int
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class MinorSkillDetailed(BaseModel):
    """Детальная информация о навыке майнера с названием"""

    skill_id: int
    skill_name: str
    required_level: int


class CourseInfo(BaseModel):
    """Базовая информация о курсе"""

    id: int
    name: str
    description: Optional[str] = None
    credits: int
    semester: Optional[int] = None

    class Config:
        from_attributes = True


class CourseWithTags(CourseInfo):
    """Курс с тегами"""

    tags: List[CourseTagSimple] = []

    class Config:
        from_attributes = True


class MinorDetailed(Minor):
    """Детальная информация о майнере с навыками и курсами"""

    target_skills: List[MinorSkillDetailed] = []
    courses: List[CourseWithTags] = []
    # Агрегированные теги майнера (из всех курсов)
    aggregated_tags: dict = Field(
        default_factory=dict, description="Теги с суммарными весами"
    )


# ============= Рекомендации майнеров =============


class MinorRecommendation(BaseModel):
    """Рекомендация майнера"""

    minor_id: int
    minor_name: str
    description: Optional[str] = None
    minor_type: Optional[str] = None
    score: float = Field(description="Оценка соответствия (чем выше, тем лучше)")
    matching_tags: List[str] = Field(
        default_factory=list, description="Совпадающие теги"
    )
    reason: str = Field(description="Причина рекомендации")


class MinorRecommendationsResponse(BaseModel):
    """Ответ с рекомендациями майнеров"""

    recommendations: List[MinorRecommendation]
    total_count: int
