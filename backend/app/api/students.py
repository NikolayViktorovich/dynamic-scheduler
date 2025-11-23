from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Specialization, User
from app.schemas.resume import ResumeResponse
from app.schemas.user import UserResponse, UserUpdate
from app.services.student import StudentService
from app.utils.dependencies import get_current_user

router = APIRouter()


@router.get("/me/profile", response_model=UserResponse)
async def get_my_profile(current_user: User = Depends(get_current_user)):
    """Получить профиль текущего студента"""
    return current_user


@router.put("/me/profile", response_model=UserResponse)
async def update_my_profile(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Обновить профиль студента"""
    if data.full_name is not None:
        current_user.full_name = data.full_name

    if data.specialization_id is not None:
        # Проверяем существование специальности
        specialization = (
            db.query(Specialization)
            .filter(Specialization.id == data.specialization_id)
            .first()
        )
        if not specialization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Specialization not found"
            )
        current_user.specialization_id = data.specialization_id

    db.commit()
    db.refresh(current_user)
    return current_user


@router.put("/me/specialization", response_model=UserResponse)
async def set_specialization(
    specialization_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Выбрать или сменить специальность"""
    # Проверяем существование специальности
    specialization = (
        db.query(Specialization).filter(Specialization.id == specialization_id).first()
    )

    if not specialization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Specialization not found"
        )

    current_user.specialization_id = specialization_id
    db.commit()
    db.refresh(current_user)

    return current_user


@router.get("/me/courses")
async def get_my_courses(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Получить курсы студента: завершенные, текущие и доступные"""
    return StudentService.get_student_courses(db, current_user)


@router.get("/me/progress")
async def get_my_progress(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Получить прогресс обучения студента"""
    return StudentService.get_student_progress(db, current_user)


@router.get("/me/resume", response_model=ResumeResponse)
async def get_my_resume(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Получить резюме студента на основе изученных курсов и навыков"""
    return StudentService.generate_resume(db, current_user)
