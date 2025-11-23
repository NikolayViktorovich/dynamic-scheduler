from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.specialization import (
    SpecializationResponse, SpecializationCreate,
    RoadmapResponse, SkillsMatrixResponse
)
from app.services.specialization import SpecializationService
from app.utils.dependencies import get_current_user
from app.models import User

router = APIRouter()


@router.get("/", response_model=List[SpecializationResponse])
async def get_all_specializations(db: Session = Depends(get_db)):
    """Получить список всех специальностей"""
    specializations = SpecializationService.get_all(db)
    return specializations


@router.get("/{specialization_id}", response_model=SpecializationResponse)
async def get_specialization(specialization_id: int, db: Session = Depends(get_db)):
    """Получить детальную информацию о специальности"""
    specialization = SpecializationService.get_by_id(db, specialization_id)
    if not specialization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Specialization not found"
        )
    return specialization


@router.get("/{specialization_id}/roadmap", response_model=RoadmapResponse)
async def get_specialization_roadmap(specialization_id: int, db: Session = Depends(get_db)):
    """Получить roadmap специальности на весь период обучения"""
    roadmap = SpecializationService.get_roadmap(db, specialization_id)
    if not roadmap:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Specialization not found or has no courses"
        )
    return roadmap


@router.get("/{specialization_id}/skills-matrix", response_model=SkillsMatrixResponse)
async def get_skills_matrix(
    specialization_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """Получить матрицу требуемых навыков для специальности"""
    skills_matrix = SpecializationService.get_skills_matrix(db, specialization_id, current_user)
    if not skills_matrix:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Specialization not found or has no required skills"
        )
    return skills_matrix


@router.post("/", response_model=SpecializationResponse, status_code=status.HTTP_201_CREATED)
async def create_specialization(
    data: SpecializationCreate,
    db: Session = Depends(get_db)
):
    """Создать новую специальность (для администраторов)"""
    specialization = SpecializationService.create(db, data)
    return specialization

