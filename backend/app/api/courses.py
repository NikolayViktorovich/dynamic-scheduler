from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.course import (
    CourseResponse, CourseDetailResponse, CourseEnrollRequest,
    CourseCompleteRequest, StudentCourseResponse
)
from app.services.course import CourseService
from app.utils.dependencies import get_current_user
from app.models import User

router = APIRouter()


@router.get("/", response_model=List[CourseResponse])
async def get_all_courses(
    specialization_id: Optional[int] = Query(None, description="Фильтр по специальности"),
    semester: Optional[int] = Query(None, description="Фильтр по семестру"),
    is_elective: Optional[bool] = Query(None, description="Фильтр по типу курса"),
    db: Session = Depends(get_db)
):
    """Получить список курсов с фильтрами"""
    courses = CourseService.get_all(db, specialization_id, semester, is_elective)
    return courses


@router.get("/my", response_model=List[StudentCourseResponse])
async def get_my_courses(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить курсы текущего студента"""
    return CourseService.get_student_courses(db, current_user)


@router.get("/{course_id}", response_model=CourseDetailResponse)
async def get_course_detail(course_id: int, db: Session = Depends(get_db)):
    """Получить детальную информацию о курсе"""
    course = CourseService.get_detail(db, course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    return course


@router.get("/{course_id}/skills", response_model=CourseDetailResponse)
async def get_course_skills(course_id: int, db: Session = Depends(get_db)):
    """Получить навыки курса по уровням сложности"""
    course = CourseService.get_detail(db, course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    return course


@router.post("/{course_id}/enroll", response_model=StudentCourseResponse)
async def enroll_in_course(
    course_id: int,
    request: CourseEnrollRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Записаться на курс"""
    return CourseService.enroll_student(db, course_id, current_user, request)


@router.put("/{course_id}/complete", response_model=StudentCourseResponse)
async def complete_course(
    course_id: int,
    request: CourseCompleteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Завершить курс"""
    return CourseService.complete_course(db, course_id, current_user, request)

