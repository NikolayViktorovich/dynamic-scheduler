from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import HTTPException, status
from app.models import Course, StudentCourse, CourseSkill, Skill, User, StudentSkill, CourseDependency
from app.models.student_course import CourseStatus
from app.schemas.course import (
    CourseCreate, CourseDetailResponse, SkillInCourse,
    CourseEnrollRequest, CourseCompleteRequest, StudentCourseResponse
)


class CourseService:
    """Сервис для работы с курсами"""
    
    @staticmethod
    def get_all(
        db: Session,
        specialization_id: Optional[int] = None,
        semester: Optional[int] = None,
        is_elective: Optional[bool] = None
    ) -> List[Course]:
        """Получить все курсы с фильтрами"""
        query = db.query(Course)
        
        if specialization_id is not None:
            query = query.filter(Course.specialization_id == specialization_id)
        if semester is not None:
            query = query.filter(Course.semester == semester)
        if is_elective is not None:
            query = query.filter(Course.is_elective == is_elective)
        
        return query.all()
    
    @staticmethod
    def get_by_id(db: Session, course_id: int) -> Optional[Course]:
        """Получить курс по ID"""
        return db.query(Course).filter(Course.id == course_id).first()
    
    @staticmethod
    def get_detail(db: Session, course_id: int) -> Optional[CourseDetailResponse]:
        """Получить детальную информацию о курсе"""
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            return None
        
        # Получаем навыки курса
        course_skills = db.query(CourseSkill, Skill).join(
            Skill, CourseSkill.skill_id == Skill.id
        ).filter(CourseSkill.course_id == course_id).all()
        
        skills_list = [
            SkillInCourse(
                skill_id=skill.id,
                skill_name=skill.name,
                difficulty_level=cs.difficulty_level,
                skill_weight=cs.skill_weight
            )
            for cs, skill in course_skills
        ]
        
        return CourseDetailResponse(
            id=course.id,
            name=course.name,
            description=course.description,
            credits=course.credits,
            semester=course.semester,
            is_elective=course.is_elective,
            specialization_id=course.specialization_id,
            difficulty_levels=course.difficulty_levels,
            skills=skills_list
        )
    
    @staticmethod
    def enroll_student(
        db: Session,
        course_id: int,
        user: User,
        request: CourseEnrollRequest
    ) -> StudentCourseResponse:
        """Записать студента на курс"""
        # Проверяем существование курса
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )
        
        # Проверяем, не записан ли уже студент на этот курс
        existing = db.query(StudentCourse).filter(
            and_(
                StudentCourse.student_id == user.id,
                StudentCourse.course_id == course_id,
                StudentCourse.status.in_([CourseStatus.ENROLLED, CourseStatus.IN_PROGRESS])
            )
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Already enrolled in this course"
            )
        
        # Проверяем пререквизиты (упрощенная проверка)
        dependencies = db.query(CourseDependency).filter(
            CourseDependency.course_id == course_id,
            CourseDependency.is_hard_dependency == True
        ).all()
        
        for dep in dependencies:
            completed = db.query(StudentCourse).filter(
                and_(
                    StudentCourse.student_id == user.id,
                    StudentCourse.course_id == dep.prerequisite_id,
                    StudentCourse.status == CourseStatus.COMPLETED
                )
            ).first()
            
            if not completed:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Prerequisite course {dep.prerequisite_id} not completed"
                )
        
        # Создаем запись
        student_course = StudentCourse(
            student_id=user.id,
            course_id=course_id,
            status=CourseStatus.ENROLLED,
            difficulty_level=request.difficulty_level
        )
        db.add(student_course)
        db.commit()
        db.refresh(student_course)
        
        return StudentCourseResponse(
            id=student_course.id,
            course_id=course.id,
            course_name=course.name,
            status=student_course.status,
            difficulty_level=student_course.difficulty_level,
            grade=student_course.grade,
            enrolled_at=student_course.enrolled_at,
            completed_at=student_course.completed_at,
            credits=course.credits
        )
    
    @staticmethod
    def complete_course(
        db: Session,
        course_id: int,
        user: User,
        request: CourseCompleteRequest
    ) -> StudentCourseResponse:
        """Завершить курс"""
        # Находим запись студента на курс
        student_course = db.query(StudentCourse).filter(
            and_(
                StudentCourse.student_id == user.id,
                StudentCourse.course_id == course_id,
                StudentCourse.status.in_([CourseStatus.ENROLLED, CourseStatus.IN_PROGRESS])
            )
        ).first()
        
        if not student_course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course enrollment not found"
            )
        
        course = db.query(Course).filter(Course.id == course_id).first()
        
        # Обновляем статус
        student_course.status = CourseStatus.COMPLETED
        student_course.grade = request.grade
        student_course.completed_at = datetime.utcnow()
        
        # Добавляем навыки студенту
        CourseService._add_skills_to_student(db, course_id, user.id, student_course.difficulty_level)
        
        db.commit()
        db.refresh(student_course)
        
        return StudentCourseResponse(
            id=student_course.id,
            course_id=course.id,
            course_name=course.name,
            status=student_course.status,
            difficulty_level=student_course.difficulty_level,
            grade=student_course.grade,
            enrolled_at=student_course.enrolled_at,
            completed_at=student_course.completed_at,
            credits=course.credits
        )
    
    @staticmethod
    def _add_skills_to_student(db: Session, course_id: int, student_id: int, difficulty_level: int):
        """Добавить навыки студенту после завершения курса"""
        # Получаем навыки курса для данного уровня сложности
        course_skills = db.query(CourseSkill).filter(
            and_(
                CourseSkill.course_id == course_id,
                CourseSkill.difficulty_level <= difficulty_level
            )
        ).all()
        
        for cs in course_skills:
            # Проверяем, есть ли уже этот навык у студента
            student_skill = db.query(StudentSkill).filter(
                and_(
                    StudentSkill.student_id == student_id,
                    StudentSkill.skill_id == cs.skill_id
                )
            ).first()
            
            if student_skill:
                # Увеличиваем уровень
                student_skill.level += cs.skill_weight
            else:
                # Создаем новый навык
                student_skill = StudentSkill(
                    student_id=student_id,
                    skill_id=cs.skill_id,
                    level=cs.skill_weight,
                    acquired_from=f"course_{course_id}"
                )
                db.add(student_skill)
        
        db.commit()
    
    @staticmethod
    def get_student_courses(db: Session, user: User) -> List[StudentCourseResponse]:
        """Получить все курсы студента"""
        student_courses = db.query(StudentCourse, Course).join(
            Course, StudentCourse.course_id == Course.id
        ).filter(StudentCourse.student_id == user.id).all()
        
        result = []
        for sc, course in student_courses:
            result.append(StudentCourseResponse(
                id=sc.id,
                course_id=course.id,
                course_name=course.name,
                status=sc.status,
                difficulty_level=sc.difficulty_level,
                grade=sc.grade,
                enrolled_at=sc.enrolled_at,
                completed_at=sc.completed_at,
                credits=course.credits
            ))
        
        return result

