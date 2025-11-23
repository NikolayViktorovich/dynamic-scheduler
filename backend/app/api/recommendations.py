from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.recommendation import (
    RecommendationsResponse, WhatIfRequest, WhatIfResponse
)
from app.services.recommendation import RecommendationService
from app.utils.dependencies import get_current_user
from app.models import User

router = APIRouter()


@router.get("/courses", response_model=RecommendationsResponse)
async def get_course_recommendations(
    limit: int = Query(5, ge=1, le=20, description="Количество рекомендаций"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получить рекомендации курсов.
    На первом этапе возвращает случайные курсы, восполняющие дефицит навыков.
    """
    recommendations = RecommendationService.get_recommendations(db, current_user, limit)
    return recommendations


@router.post("/what-if", response_model=WhatIfResponse)
async def what_if_specialization_change(
    request: WhatIfRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Моделирование смены специальности.
    Показывает, как изменится профиль навыков при переходе на другую специальность.
    """
    result = RecommendationService.what_if_analysis(db, current_user, request)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Specialization not found"
        )
    
    return result

