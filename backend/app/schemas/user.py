from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Базовая схема пользователя"""

    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=100)


class UserCreate(UserBase):
    """Схема для создания пользователя"""

    password: str = Field(..., min_length=6, max_length=100)


class UserLogin(BaseModel):
    """Схема для входа"""

    email: EmailStr
    password: str


class UserResponse(UserBase):
    """Схема ответа с данными пользователя"""

    id: int
    is_active: bool
    specialization_id: Optional[int] = None
    minor_ids: List[int] = []
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Схема ответа с токенами"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    """Схема для обновления токена"""

    refresh_token: str


class UserUpdate(BaseModel):
    """Схема для обновления профиля пользователя"""

    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    specialization_id: Optional[int] = None


class PasswordChange(BaseModel):
    """Схема для смены пароля (требует текущий пароль)"""

    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=6, max_length=100)
    confirm_password: str = Field(..., min_length=6, max_length=100)


class PasswordChangeResponse(BaseModel):
    """Схема ответа после смены пароля"""

    message: str
    success: bool
