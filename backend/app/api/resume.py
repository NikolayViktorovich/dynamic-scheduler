"""API эндпоинт для генерации резюме студента"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas.resume import ResumeResponse
from app.services.resume_service import ResumeService
from app.utils.dependencies import get_current_user

router = APIRouter()


@router.get("/", response_model=ResumeResponse)
def get_my_resume(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Получить текущее резюме студента.

    Резюме включает:
    - личную информацию (имя, email, основная специальность)
    - все навыки студента из:
      - основной специальности (core)
      - всех майнеров, включая архивные (orbit)
    - информацию о майнерах (текущие и завершённые)
    - статистику образования (курсы, кредиты)
    - достижения

    **Важно**: даже если майнер был изменён (archived),
    все навыки из него остаются в резюме!

    Это резюме можно сгенерировать в любой момент обучения
    или по окончании основной специальности как итоговое.
    """
    resume = ResumeService.generate_resume(db, current_user)
    return resume
