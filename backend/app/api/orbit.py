"""API эндпоинт для орбиты студента"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas.orbit import OrbitResponse
from app.services.orbit_service import OrbitService
from app.utils.dependencies import get_current_user

router = APIRouter()


@router.get("/", response_model=OrbitResponse)
def get_my_orbit(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Получить орбиту текущего студента.

    Орбита показывает:
    - выбранный майнер (дополнительное образование)
    - целевые навыки майнера (что нужно освоить)
    - курсы майнера с отметкой о прохождении
    - прогресс (процент пройденных курсов)

    **Важно**: орбита НЕ показывает текущие уровни навыков студента явно,
    только цели майнера и прогресс по курсам.

    Если у студента нет выбранного майнера, возвращается 404.
    """
    orbit = OrbitService.get_orbit(db, current_user)

    if not orbit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="У студента нет выбранного майнера. Выберите майнер через /api/minors/select",
        )

    return orbit
