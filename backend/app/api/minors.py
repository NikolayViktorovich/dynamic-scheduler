"""API эндпоинты для майнеров"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Minor, User, UserMinor
from app.schemas.minor import (
    Minor as MinorSchema,
)
from app.schemas.minor import (
    MinorDetailed,
    MinorRecommendationsResponse,
    UserMinorCreate,
)
from app.schemas.minor import (
    UserMinor as UserMinorSchema,
)
from app.services.minor_service import MinorRecommendationService
from app.services.orbit_service import OrbitService
from app.utils.dependencies import get_current_user

router = APIRouter()


@router.get("/", response_model=List[MinorSchema])
def get_all_minors(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    include_inactive: bool = Query(False),
    db: Session = Depends(get_db),
):
    """
    Получить список всех майнеров.

    - **skip**: количество записей для пропуска (пагинация)
    - **limit**: максимальное количество записей
    - **include_inactive**: включать ли неактивные майнеры
    """
    query = db.query(Minor)

    if not include_inactive:
        query = query.filter(Minor.is_active == True)

    minors = query.offset(skip).limit(limit).all()
    return minors


@router.get("/{minor_id}", response_model=MinorDetailed)
def get_minor_by_id(minor_id: int, db: Session = Depends(get_db)):
    """
    Получить детальную информацию о майнере.

    Включает:
    - целевые навыки майнера
    - курсы, входящие в майнер
    - агрегированные теги
    """
    minor_detailed = MinorRecommendationService.get_minor_detailed(db, minor_id)

    if not minor_detailed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Minor with id {minor_id} not found",
        )

    return minor_detailed


@router.get("/recommendations/for-me", response_model=MinorRecommendationsResponse)
def get_minor_recommendations(
    limit: int = Query(5, ge=1, le=20, description="Количество рекомендаций"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Получить рекомендации майнеров для текущего студента.

    Рекомендации основаны на:
    - дифференцированных тегах (с весами)
    - пройденных курсах студента
    - интересах и профиле студента

    Возвращает майнеры, отсортированные по score (релевантности).
    """
    recommendations = MinorRecommendationService.get_recommendations(
        db, current_user, limit
    )
    return recommendations


@router.get("/recommendations/similar", response_model=MinorRecommendationsResponse)
def get_similar_minors(
    current_minor_id: int = Query(..., description="ID текущего майнера"),
    limit: int = Query(3, ge=1, le=10),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Получить рекомендации похожих майнеров при смене текущего.

    Используется, когда студент хочет сменить майнер —
    система предлагает похожие направления на основе:
    - текущего выбранного майнера
    - уже пройденных курсов
    """
    recommendations = MinorRecommendationService.get_similar_minors_on_change(
        db, current_user, current_minor_id, limit
    )
    return recommendations


@router.post(
    "/select", response_model=UserMinorSchema, status_code=status.HTTP_201_CREATED
)
def select_minor(
    minor_data: UserMinorCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Выбрать майнер для студента.

    Если у студента уже выбран другой майнер (status=selected),
    старый майнер будет переведён в статус 'archived',
    а все полученные навыки останутся в резюме.
    """
    try:
        user_minor = OrbitService.select_minor(db, current_user, minor_data.minor_id)
        return user_minor
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{minor_id}/complete", response_model=UserMinorSchema)
def complete_minor(
    minor_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Отметить майнер как завершённый.

    После завершения майнера:
    - навыки остаются в профиле студента
    - майнер отмечается как 'completed' в резюме
    - можно выбрать новый майнер
    """
    user_minor = OrbitService.complete_minor(db, current_user, minor_id)

    if not user_minor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Selected minor with id {minor_id} not found for current user",
        )

    return user_minor


@router.get("/my/history", response_model=List[UserMinorSchema])
def get_my_minors(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Получить историю майнеров студента.

    Включает:
    - текущий выбранный (selected)
    - завершённые (completed)
    - архивные (archived)
    """
    user_minors = db.query(UserMinor).filter(UserMinor.user_id == current_user.id).all()

    return user_minors
