"""Pydantic схемы для валидации данных"""

from app.schemas.minor import (
    Minor,
    MinorCreate,
    MinorDetailed,
    MinorRecommendation,
    MinorRecommendationsResponse,
    MinorUpdate,
    UserMinor,
    UserMinorCreate,
    UserMinorUpdate,
)
from app.schemas.orbit import (
    OrbitCourse,
    OrbitResponse,
    TargetSkill,
)
from app.schemas.resume import (
    ResumeEducation,
    ResumeMinor,
    ResumePersonalInfo,
    ResumeResponse,
    ResumeSkill,
)
from app.schemas.user import (
    PasswordChange,
    PasswordChangeResponse,
    TokenRefresh,
    TokenResponse,
    UserBase,
    UserCreate,
    UserLogin,
    UserResponse,
    UserUpdate,
)

__all__ = [
    "UserBase",
    "UserCreate",
    "UserLogin",
    "UserResponse",
    "TokenResponse",
    "TokenRefresh",
    "UserUpdate",
    "PasswordChange",
    "PasswordChangeResponse",
    "ResumePersonalInfo",
    "ResumeSkill",
    "ResumeEducation",
    "ResumeResponse",
    "ResumeMinor",
    "Minor",
    "MinorCreate",
    "MinorUpdate",
    "MinorDetailed",
    "MinorRecommendation",
    "MinorRecommendationsResponse",
    "UserMinor",
    "UserMinorCreate",
    "UserMinorUpdate",
    "OrbitResponse",
    "OrbitCourse",
    "TargetSkill",
]
