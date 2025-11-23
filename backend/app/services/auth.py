from typing import Optional

from sqlalchemy.orm import Session

from app.models import User
from app.schemas.user import UserCreate
from app.utils.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
)


class AuthService:
    """Сервис аутентификации"""

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """Аутентификация пользователя"""
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """Создание нового пользователя"""
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Получение пользователя по email"""
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def create_tokens(user_id: int) -> dict:
        """Создание access и refresh токенов"""
        access_token = create_access_token(data={"sub": str(user_id)})
        refresh_token = create_refresh_token(data={"sub": str(user_id)})
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    @staticmethod
    def change_password(
        db: Session, user: User, current_password: str, new_password: str
    ) -> bool:
        """
        Смена пароля пользователя.

        Args:
            db: Сессия базы данных
            user: Объект пользователя
            current_password: Текущий пароль
            new_password: Новый пароль

        Returns:
            True если пароль успешно изменен, False если текущий пароль неверен
        """
        # Проверяем текущий пароль
        if not verify_password(current_password, user.hashed_password):
            return False

        # Хешируем и сохраняем новый пароль
        user.hashed_password = get_password_hash(new_password)
        db.commit()
        return True
