from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.skill import (
    SkillResponse, SkillTreeNode, StudentSkillResponse, GapAnalysisResponse
)
from app.services.skill import SkillService
from app.utils.dependencies import get_current_user
from app.models import User

router = APIRouter()


@router.get("/", response_model=List[SkillResponse])
async def get_all_skills(db: Session = Depends(get_db)):
    """Получить список всех навыков"""
    skills = SkillService.get_all(db)
    return skills


@router.get("/tree", response_model=List[SkillTreeNode])
async def get_skills_tree(db: Session = Depends(get_db)):
    """Получить древовидную структуру всех навыков"""
    tree = SkillService.get_tree(db)
    return tree


@router.get("/my-skills", response_model=List[StudentSkillResponse])
async def get_my_skills(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить текущие навыки студента"""
    return SkillService.get_student_skills(db, current_user)


@router.get("/gap-analysis", response_model=GapAnalysisResponse)
async def get_gap_analysis(
    specialization_id: Optional[int] = Query(
        None,
        description="ID специальности для анализа (если не указан, используется специальность студента)"
    ),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Анализ дефицита навыков для выбранной специальности"""
    analysis = SkillService.gap_analysis(db, current_user, specialization_id)
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Specialization not found or not selected"
        )
    
    return analysis

