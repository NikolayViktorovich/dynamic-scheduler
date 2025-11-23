"""Сервис для работы с орбитой студента"""

from typing import Optional

from sqlalchemy.orm import Session

from app.models import (
    Course,
    CourseTag,
    Minor,
    MinorCourse,
    MinorSkill,
    Skill,
    StudentCourse,
    User,
    UserMinor,
)
from app.models.student_course import CourseStatus
from app.schemas.orbit import OrbitCourse, OrbitResponse, TargetSkill


class OrbitService:
    """Сервис для получения орбиты студента (цель и структура майнера)"""

    @staticmethod
    def get_orbit(db: Session, user: User) -> Optional[OrbitResponse]:
        """
        Получить орбиту студента.

        Орбита = текущий выбранный майнер с:
        - целевыми навыками майнера
        - курсами майнера (с отметкой о прохождении студентом)

        НЕ показываем текущие уровни навыков студента явно,
        только цель майнера и прогресс по курсам.
        """
        # Получаем текущий выбранный майнер студента
        user_minor = (
            db.query(UserMinor)
            .filter(UserMinor.user_id == user.id, UserMinor.status == "selected")
            .first()
        )

        if not user_minor:
            return None

        minor = db.query(Minor).filter(Minor.id == user_minor.minor_id).first()
        if not minor:
            return None

        # Получаем целевые навыки майнера
        minor_skills = (
            db.query(MinorSkill, Skill)
            .join(Skill, MinorSkill.skill_id == Skill.id)
            .filter(MinorSkill.minor_id == minor.id)
            .all()
        )

        target_skills = [
            TargetSkill(
                skill_id=ms.skill_id,
                skill_name=skill.name,
                skill_description=skill.description,
                required_level=ms.required_level,
            )
            for ms, skill in minor_skills
        ]

        # Получаем курсы майнера
        minor_courses = (
            db.query(MinorCourse, Course)
            .join(Course, MinorCourse.course_id == Course.id)
            .filter(MinorCourse.minor_id == minor.id)
            .order_by(MinorCourse.order)
            .all()
        )

        # Получаем пройденные курсы студента
        completed_course_ids = set(
            [
                sc.course_id
                for sc in db.query(StudentCourse)
                .filter(
                    StudentCourse.student_id == user.id,
                    StudentCourse.status == CourseStatus.COMPLETED,
                )
                .all()
            ]
        )

        # Формируем список курсов с отметкой о прохождении
        orbit_courses = []
        completed_count = 0

        for mc, course in minor_courses:
            is_completed = course.id in completed_course_ids
            if is_completed:
                completed_count += 1

            # Получаем теги курса
            tags = db.query(CourseTag).filter(CourseTag.course_id == course.id).all()
            course_tags = [
                {"tag_name": tag.tag_name, "weight": tag.weight} for tag in tags
            ]

            orbit_courses.append(
                OrbitCourse(
                    course_id=course.id,
                    course_name=course.name,
                    description=course.description,
                    credits=course.credits,
                    semester=course.semester,
                    order=mc.order,
                    is_required=mc.is_required,
                    is_completed=is_completed,
                    tags=course_tags,
                )
            )

        # Статистика
        total_courses = len(orbit_courses)
        progress_percentage = (
            (completed_count / total_courses * 100) if total_courses > 0 else 0.0
        )

        return OrbitResponse(
            minor_id=minor.id,
            minor_name=minor.name,
            minor_description=minor.description,
            minor_type=minor.minor_type,
            target_skills=target_skills,
            courses=orbit_courses,
            total_courses=total_courses,
            completed_courses=completed_count,
            progress_percentage=round(progress_percentage, 2),
        )

    @staticmethod
    def select_minor(db: Session, user: User, minor_id: int) -> UserMinor:
        """
        Выбрать майнер для студента.

        Если у студента уже есть выбранный майнер (status=selected),
        старый майнер переводится в статус 'archived'.
        """
        # Проверяем, что майнер существует
        minor = db.query(Minor).filter(Minor.id == minor_id).first()
        if not minor:
            raise ValueError(f"Minor with id {minor_id} not found")

        # Архивируем текущий выбранный майнер (если есть)
        current_user_minor = (
            db.query(UserMinor)
            .filter(UserMinor.user_id == user.id, UserMinor.status == "selected")
            .first()
        )

        if current_user_minor:
            current_user_minor.status = "archived"
            db.add(current_user_minor)

        # Создаём новую запись для выбранного майнера
        new_user_minor = UserMinor(
            user_id=user.id, minor_id=minor_id, status="selected"
        )
        db.add(new_user_minor)
        db.commit()
        db.refresh(new_user_minor)

        return new_user_minor

    @staticmethod
    def complete_minor(db: Session, user: User, minor_id: int) -> Optional[UserMinor]:
        """Отметить майнер как завершённый"""
        user_minor = (
            db.query(UserMinor)
            .filter(
                UserMinor.user_id == user.id,
                UserMinor.minor_id == minor_id,
                UserMinor.status == "selected",
            )
            .first()
        )

        if not user_minor:
            return None

        user_minor.status = "completed"
        db.add(user_minor)
        db.commit()
        db.refresh(user_minor)

        return user_minor
